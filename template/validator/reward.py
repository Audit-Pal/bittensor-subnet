# import numpy as np
# import json
# import bittensor as bt
# from typing import List, Optional, Dict, Any
# from pathlib import Path

# from template.protocol import AgentSubmission
# from template.validator.agent_runner import wrun_github_agent
# from template.validator.scoring import score_with_ground_truth


# def reward(
#     response: Optional[AgentSubmission],
#     challenge: Dict[str, Any],
#     ground_truth: Optional[Dict[str, Any]],
#     agent_timeout: int,
#     temp_dir: Path,
#     miner_uid: int,
# ) -> float:
#     """
#     Compute reward for a single miner by running their agent
#     and scoring against ground_truth.
    
#     FIXED ISSUES:
#     1. Changed response.repo_url to response.github_url
#     2. Added ground_truth parameter instead of reading from file
#     3. Added temp_dir for file isolation
#     4. Added miner_uid for unique file naming
#     5. Better error handling and logging
#     6. Proper None checks
    
#     Args:
#         response: Miner's response containing github_url
#         challenge: Challenge data to send to agent
#         ground_truth: Ground truth data for scoring (can be None)
#         agent_timeout: Seconds to allow agent execution
#         temp_dir: Temporary directory for this validation round
#         miner_uid: UID of the miner being evaluated
        
#     Returns:
#         float: Score in [0.0, 1.0]
#     """

#     # Validate response
#     if response is None:
#         bt.logging.debug(f"Miner {miner_uid}: response is None")
#         return 0.0
    
#     if not hasattr(response, 'github_url'):
#         bt.logging.warning(f"Miner {miner_uid}: response missing github_url attribute")
#         return 0.0
        
#     if not response.github_url:
#         bt.logging.warning(f"Miner {miner_uid}: empty github_url")
#         return 0.0

#     # Validate challenge
#     if not challenge or not isinstance(challenge, dict):
#         bt.logging.error(f"Miner {miner_uid}: invalid challenge data")
#         return 0.0

#     try:
#         repo_url = response.github_url.strip()
        
#         # Basic URL validation
#         if not repo_url.startswith(("https://github.com/", "http://github.com/")):
#             bt.logging.warning(f"Miner {miner_uid}: invalid GitHub URL format: {repo_url}")
#             return 0.0

#         # Use stable identifier if available
#         challenge_id = challenge.get("project_id", "unknown")

#         # Create unique file paths in temp directory
#         input_file = temp_dir / f"input_miner_{miner_uid}.json"
#         output_file = temp_dir / f"output_miner_{miner_uid}.json"
#         ground_truth_file = temp_dir / "ground_truth.json"

#         # -------------------------------
#         # Write input.json for agent
#         # -------------------------------
#         try:
#             with open(input_file, "w") as f:
#                 json.dump(challenge, f, indent=2)
#         except IOError as e:
#             bt.logging.error(f"Miner {miner_uid}: failed to write input file: {e}")
#             return 0.0

#         # -------------------------------
#         # Write ground truth if available
#         # -------------------------------
#         if ground_truth:
#             try:
#                 with open(ground_truth_file, "w") as f:
#                     json.dump(ground_truth, f, indent=2)
#             except IOError as e:
#                 bt.logging.warning(f"Miner {miner_uid}: failed to write ground truth: {e}")

#         # -------------------------------
#         # Run agent
#         # -------------------------------
#         bt.logging.info(f"Miner {miner_uid}: Running agent from {repo_url}")
        
#         agent_output = wrun_github_agent(
#             repo_url=repo_url,
#             task_file=str(input_file),
#             output_file=str(output_file),
#             agent_timeout=agent_timeout,
#         )

#         if agent_output is None:
#             bt.logging.info(f"Miner {miner_uid}: agent execution failed")
#             return 0.0

#         # -------------------------------
#         # Score vs ground truth
#         # -------------------------------
#         if not ground_truth:
#             bt.logging.warning(f"Miner {miner_uid}: no ground truth available, returning 0")
#             return 0.0

#         score = score_with_ground_truth(
#             agent_output=agent_output,
#             ground_truth_path=str(ground_truth_file)
#         )

#         bt.logging.info(f"Miner {miner_uid}: scored {score:.4f}")
        
#         # Ensure score is in valid range
#         return float(max(0.0, min(1.0, score)))

#     except Exception as e:
#         bt.logging.error(f"Miner {miner_uid}: reward exception: {e}")
#         return 0.0


# def get_rewards(
#     self,
#     responses: List[Optional[AgentSubmission]],
#     challenge: Dict[str, Any],
#     ground_truth: Optional[Dict[str, Any]],
#     temp_dir: Path,
#     miner_uids: List[int],
# ) -> np.ndarray:
#     """
#     Compute rewards for a batch of miner responses.
    
#     FIXED ISSUES:
#     1. Added ground_truth parameter
#     2. Added temp_dir parameter
#     3. Added miner_uids parameter for better logging
#     4. Proper validation of inputs
#     5. Better error handling
    
#     Args:
#         self: Validator instance
#         responses: List of miner responses
#         challenge: Challenge data
#         ground_truth: Ground truth data (can be None)
#         temp_dir: Temporary directory for file operations
#         miner_uids: List of miner UIDs corresponding to responses
        
#     Returns:
#         np.ndarray: Array of rewards in [0.0, 1.0]
#     """

#     # Validate inputs
#     if not responses:
#         bt.logging.warning("get_rewards: empty responses list")
#         return np.array([], dtype=np.float32)
    
#     if len(responses) != len(miner_uids):
#         bt.logging.error(
#             f"get_rewards: responses length ({len(responses)}) != "
#             f"miner_uids length ({len(miner_uids)})"
#         )
#         return np.zeros(len(responses), dtype=np.float32)

#     agent_timeout = getattr(self.config.neuron, 'agent_timeout', 60)
#     rewards = np.zeros(len(responses), dtype=np.float32)

#     bt.logging.info(f"Computing rewards for {len(responses)} miners")

#     for i, response in enumerate(responses):
#         miner_uid = miner_uids[i]
        
#         try:
#             rewards[i] = reward(
#                 response=response,
#                 challenge=challenge,
#                 ground_truth=ground_truth,
#                 agent_timeout=agent_timeout,
#                 temp_dir=temp_dir,
#                 miner_uid=miner_uid,
#             )
#         except Exception as e:
#             bt.logging.error(f"Miner {miner_uid}: failed to compute reward: {e}")
#             rewards[i] = 0.0

#     bt.logging.info(f"Rewards computed: {rewards}")
    
#     return rewards
import numpy as np
import json
import bittensor as bt
from typing import List, Optional, Dict, Any
from pathlib import Path

from template.protocol import AgentSubmission
from template.validator.agent_runner import wrun_github_agent


def reward(
    response: Optional[AgentSubmission],
    challenge: Dict[str, Any],
    temp_dir: Path,
    miner_uid: int,
) -> float:
    """
    Simplified reward function for testing.
    Simply runs the agent and writes output to output.json
    
    Args:
        response: Miner's response containing github_url
        challenge: Challenge data to send to agent
        temp_dir: Temporary directory for this validation round
        miner_uid: UID of the miner being evaluated
        
    Returns:
        float: 1.0 if successful, 0.0 if failed
    """

    # Validate response
    if response is None:
        bt.logging.debug(f"Miner {miner_uid}: response is None")
        return 0.0
    
    if not hasattr(response, 'github_url'):
        bt.logging.warning(f"Miner {miner_uid}: response missing github_url attribute")
        return 0.0
        
    if not response.github_url:
        bt.logging.warning(f"Miner {miner_uid}: empty github_url")
        return 0.0

    # Validate challenge
    if not challenge or not isinstance(challenge, dict):
        bt.logging.error(f"Miner {miner_uid}: invalid challenge data")
        return 0.0

    try:
        repo_url = response.github_url.strip()
        
        # Basic URL validation
        if not repo_url.startswith(("https://github.com/", "http://github.com/")):
            bt.logging.warning(f"Miner {miner_uid}: invalid GitHub URL format: {repo_url}")
            return 0.0

        # Create unique file paths in temp directory
        input_file = temp_dir / f"input_miner_{miner_uid}.json"
        output_file = temp_dir / f"output_miner_{miner_uid}.json"

        # Write input.json for agent
        try:
            with open(input_file, "w") as f:
                json.dump(challenge, f, indent=2)
        except IOError as e:
            bt.logging.error(f"Miner {miner_uid}: failed to write input file: {e}")
            return 0.0

        # Run agent
        bt.logging.info(f"Miner {miner_uid}: Running agent from {repo_url}")
        
        agent_output = wrun_github_agent(
            repo_url=repo_url,
            task_file=str(input_file),
            output_file=str(output_file),
            agent_timeout=60,
        )

        if agent_output is None:
            bt.logging.info(f"Miner {miner_uid}: agent execution failed")
            return 0.0

        # Write output to file
        try:
            with open(output_file, "w") as f:
                json.dump(agent_output, f, indent=2)
            bt.logging.info(f"Miner {miner_uid}: output written to {output_file}")
        except IOError as e:
            bt.logging.error(f"Miner {miner_uid}: failed to write output file: {e}")
            return 0.0

        # Return success
        return 1.0

    except Exception as e:
        bt.logging.error(f"Miner {miner_uid}: reward exception: {e}")
        return 0.0


def get_rewards(
    self,
    responses: List[Optional[AgentSubmission]],
    challenge: Dict[str, Any],
    temp_dir: Path,
    miner_uids,
) -> np.ndarray:
    """
    Compute rewards for a batch of miner responses.
    
    Args:
        self: Validator instance
        responses: List of miner responses
        challenge: Challenge data
        temp_dir: Temporary directory for file operations
        miner_uids: List of miner UIDs corresponding to responses
        
    Returns:
        np.ndarray: Array of rewards (1.0 for success, 0.0 for failure)
    """

    # Validate inputs - convert to list if array
    if isinstance(miner_uids, np.ndarray):
        miner_uids = miner_uids.tolist()
    
    if len(responses) == 0:
        bt.logging.warning("get_rewards: empty responses list")
        return np.array([], dtype=np.float32)
    
    if len(responses) != len(miner_uids):
        bt.logging.error(
            f"get_rewards: responses length ({len(responses)}) != "
            f"miner_uids length ({len(miner_uids)})"
        )
        return np.zeros(len(responses), dtype=np.float32)

    rewards = np.zeros(len(responses), dtype=np.float32)

    bt.logging.info(f"Computing rewards for {len(responses)} miners")

    for i, response in enumerate(responses):
        miner_uid = miner_uids[i]
        
        try:
            rewards[i] = reward(
                response=response,
                challenge=challenge,
                temp_dir=temp_dir,
                miner_uid=miner_uid,
            )
        except Exception as e:
            bt.logging.error(f"Miner {miner_uid}: failed to compute reward: {e}")
            rewards[i] = 0.0

    bt.logging.info(f"Rewards computed: {rewards}")
    
    return rewards