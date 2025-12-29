import subprocess
import importlib.util
import tempfile
from pathlib import Path
import json
import bittensor as bt


def wrun_github_agent(repo_url: str, task_file: str, output_file: str, agent_timeout: int = 60):
    """
    Clone a GitHub repo, load agent.py, execute tasks from task_file (JSON),
    and write the results to output_file (JSON).

    Parameters:
        repo_url (str): URL of the GitHub repo containing agent.py
        task_file (str): Path to input JSON file with tasks
        output_file (str): Path where output JSON will be written
        agent_timeout (int): Max seconds to allow agent execution (default: 60)

    Returns:
        dict: Output from agent.run(tasks), or None if execution failed
    """
    try:
        # Ensure task file exists
        task_path = Path(task_file)
        if not task_path.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Clone GitHub repo into temporary directory
            subprocess.run(
                ["git", "clone", repo_url, str(temp_path)],
                check=True,
                timeout=30,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            bt.logging.info(f"Cloned repo {repo_url} successfully.")

            # Check for agent.py
            agent_path = temp_path / "agent.py"
            if not agent_path.exists():
                raise FileNotFoundError(f"agent.py not found in {repo_url}")

            # Dynamically load agent.py
            spec = importlib.util.spec_from_file_location("agent", agent_path)
            agent = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent)
            bt.logging.info("Agent loaded successfully.")

            # Read tasks from JSON
            with open(task_file, "r") as f:
                task_data = json.load(f)
            
            # Check if agent has run() function
            if not hasattr(agent, "run"):
                raise AttributeError(f"Agent from {repo_url} does not have a 'run' method")
            
            
            bt.logging.info("Running agent with task data...")
            result = agent.run(task_data)
            
            # Write output to JSON
            with open(output_file, "w") as f:
                json.dump(result, f, indent=4)

            bt.logging.info(f"Output written to {output_file}")
            return result

    except Exception as e:
        bt.logging.warning(f"Failed to run agent from {repo_url}: {e}")
        return None