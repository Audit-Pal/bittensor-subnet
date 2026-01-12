import asyncio
import json
import bittensor as bt
import requests
from pathlib import Path
import tempfile
import shutil

from template.protocol import AgentSubmission
from template.utils.uids import get_random_uids
from template.validator.agent_runner import wrun_github_agent
from template.validator.scoring import score_with_ground_truth

CHALLENGE_API = "https://audit-api-two.vercel.app/api/challenges/random"
GROUND_TRUTH_API = "https://audit-api-two.vercel.app/api/challenges/report"


async def forward(self):
    """
    VALIDATOR FORWARD FUNCTION WITH GROUND TRUTH SCORING
    
    Changes made:
    1. Fetch ground truth URL from challenge project_id
    2. Agent output is written to output.json
    3. Score agent output against ground truth findings
    4. Proper error handling and cleanup
    """
    
   
    #  Sample miners

    miner_uids = get_random_uids(
        self, k=self.config.neuron.sample_size
    )

    if len(miner_uids) == 0:
        bt.logging.warning("No miners sampled")
        return []

    # Handle both list and numpy array types
    if hasattr(miner_uids, 'tolist'):
        miner_uids = miner_uids.tolist()

    axons = [self.metagraph.axons[uid] for uid in miner_uids]
    bt.logging.info(f"Sampled {len(miner_uids)} miners: {miner_uids}")

 
    try:
        bt.logging.info("Fetching challenge from API...")
        resp = requests.get(CHALLENGE_API, timeout=10)
        resp.raise_for_status()
        challenge = resp.json()
    except requests.RequestException as e:
        bt.logging.error(f"Failed to fetch challenge: {e}")
        return []
    except json.JSONDecodeError as e:
        bt.logging.error(f"Invalid JSON in challenge response: {e}")
        return []

    # Validate challenge structure
    if not isinstance(challenge, dict):
        bt.logging.error("Challenge is not a valid dictionary")
        return []

    project_id = challenge.get("project_id")
    if not project_id:
        bt.logging.error("Challenge missing project_id")
        return []

    bt.logging.info(f"Fetched challenge: {project_id}")

    ground_truth = None
    ground_truth_url = f"{GROUND_TRUTH_API}/{project_id}"
    
    try:
        bt.logging.info(f"Fetching ground truth from: {ground_truth_url}")
        gt_resp = requests.get(ground_truth_url, timeout=10)
        gt_resp.raise_for_status()
        ground_truth = gt_resp.json()
        gt_findings = ground_truth.get("findings", [])
        bt.logging.info(f"Ground truth fetched successfully: {len(gt_findings)} findings")
    except requests.RequestException as e:
        bt.logging.warning(f"Failed to fetch ground truth: {e}")
        ground_truth = None
    except json.JSONDecodeError as e:
        bt.logging.warning(f"Invalid JSON in ground truth response: {e}")
        ground_truth = None

    # If no ground truth, cannot proceed with scoring
    if ground_truth is None:
        bt.logging.error("No ground truth available - cannot score")
        return []

  
    temp_dir = Path(tempfile.mkdtemp(prefix=f"validator_{project_id}_"))
    
    try:
        input_file = temp_dir / "task.json"
        
        # Write challenge to task file
        with open(input_file, "w") as f:
            json.dump(challenge, f, indent=2)
        bt.logging.info(f"Challenge written to {input_file}")

       
        bt.logging.info("Querying miners for GitHub URLs...")
        responses = await self.dendrite(
            axons=axons,
            synapse=AgentSubmission(
                prompt="Send GitHub repo URL containing agent.py"
            ),
            deserialize=True,
            timeout=12.0
        )

      
        rewards = [0.0] * len(miner_uids)

        for i, response in enumerate(responses):
            uid = miner_uids[i]

            # Validate response
            if response is None:
                bt.logging.warning(f"Miner {uid} returned None response")
                continue
                
            if not hasattr(response, "github_url"):
                bt.logging.warning(f"Miner {uid} response missing github_url attribute")
                continue
                
            if not response.github_url:
                bt.logging.warning(f"Miner {uid} returned empty github_url")
                continue

            repo_url = response.github_url.strip()
            
            # Basic URL validation
            if not repo_url.startswith(("https://github.com/", "http://github.com/")):
                bt.logging.warning(f"Miner {uid} provided invalid GitHub URL: {repo_url}")
                continue

            # Create unique output file for this miner
            output_file = f"output.json"

            bt.logging.info(f"Running agent from miner {uid}: {repo_url}")

            try:
                agent_output = wrun_github_agent(
                    repo_url=repo_url,
                    task_file=str(input_file),
                    output_file=str(output_file),
                    agent_timeout=self.config.neuron.agent_timeout,
                )

                if agent_output is None:
                    bt.logging.warning(f"Agent execution failed for miner {uid}")
                    rewards[i] = 0.0
                    continue

                # Write output to file
                try:
                    with open(output_file, "w") as f:
                        json.dump(agent_output, f, indent=2)
                    
                    bt.logging.info(f"Miner {uid} output written to {output_file}")
                except Exception as e:
                    bt.logging.error(f"Failed to write output file for miner {uid}: {e}")
                    rewards[i] = 0.0
                    continue

                # Score against ground truth
                try:
                    score = score_with_ground_truth(
                        agent_output=agent_output,
                        ground_truth=ground_truth
                    )
                    
                    rewards[i] = score
                    bt.logging.info(f"Miner {uid} scored: {score:.4f}")
                except Exception as e:
                    bt.logging.error(f"Failed to score miner {uid}: {e}")
                    rewards[i] = 0.0
                    continue

            except Exception as e:
                bt.logging.error(f"Error processing miner {uid}: {e}")
                rewards[i] = 0.0
                continue

        bt.logging.info(f"Updating scores for {len(miner_uids)} miners")
        bt.logging.info(f"Rewards: {rewards}")
        
        self.update_scores(rewards, miner_uids)

        try:
            shutil.rmtree(temp_dir)
            bt.logging.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            bt.logging.warning(f"Failed to cleanup temp directory: {e}")

        # Async cooldown
        sleep_time = self.config.neuron.forward_sleep or 1.0
        bt.logging.info(f"Sleeping for {sleep_time}s before next iteration")
        await asyncio.sleep(sleep_time)

        return responses
        
    except Exception as e:
        bt.logging.error(f"Critical error in forward pass: {e}")
        # Cleanup on error
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        return []