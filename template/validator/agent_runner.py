import subprocess
import importlib.util
import tempfile
from pathlib import Path
import json
import bittensor as bt
import multiprocessing as mp
import hashlib
import datetime
import os
import sys


# -------------------------------
# Expected Output Schema
# -------------------------------

REQUIRED_FIELDS = {
    "project": str,
    "timestamp": str,
    "files_analyzed": int,
    "files_skipped": int,
    "total_findings": int,
    "findings": list,
}

REQUIRED_FINDING_FIELDS = {
    "title": str,
    "description": str,
    "vulnerability_type": str,
    "severity": str,
    "confidence": (int, float),
    "location": str,
    "file": str,
    "id": str,
    "reported_by_model": str,
    "status": str,
}



def _validate_agent_output(result: dict) -> bool:
    if not isinstance(result, dict):
        return False

    for field, typ in REQUIRED_FIELDS.items():
        if field not in result or not isinstance(result[field], typ):
            return False

    for finding in result["findings"]:
        if not isinstance(finding, dict):
            return False

        for field, typ in REQUIRED_FINDING_FIELDS.items():
            if field not in finding or not isinstance(finding[field], typ):
                return False

        confidence = float(finding["confidence"])
        if confidence < 0.0 or confidence > 1.0:
            return False

    return True


def _run_agent_process(agent_path: Path, tasks: dict, api_key, return_dict):
    try:
        spec = importlib.util.spec_from_file_location("agent", agent_path)
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        if not hasattr(agent, "main"):
            raise AttributeError("agent.py must define main(tasks, api_key=None)")

        result = agent.main(tasks, api_key)
        return_dict["result"] = result

    except Exception as e:
        return_dict["error"] = str(e)



def wrun_github_agent(
    repo_url: str,
    task_file: str,
    output_file: str,
    api_key: str | None = None,
    agent_timeout: int = 60,
):
    """
    Securely clone a miner repo, execute agent.py in isolation,
    validate output, and write results to output_file.
    """

    try:
        task_path = Path(task_file)
        if not task_path.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Clone repo (shallow clone)
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(temp_path)],
                check=True,
                timeout=30,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            bt.logging.info(f"Cloned repo: {repo_url}")

            agent_path = temp_path / "agent.py"
            if not agent_path.exists():
                raise FileNotFoundError("agent.py not found in repository")

            # Hash agent code for auditability
            agent_hash = hashlib.sha256(agent_path.read_bytes()).hexdigest()

            # Load task JSON
            with open(task_file, "r") as f:
                tasks = json.load(f)

            manager = mp.Manager()
            return_dict = manager.dict()

            process = mp.Process(
                target=_run_agent_process,
                args=(agent_path, tasks, api_key, return_dict),
            )

            process.start()
            process.join(timeout=agent_timeout)

            if process.is_alive():
                process.terminate()
                process.join()
                bt.logging.warning("Agent execution timed out")
                return None

            if "error" in return_dict:
                bt.logging.warning(f"Agent execution error: {return_dict['error']}")
                return None

            result = return_dict.get("result")

            if not _validate_agent_output(result):
                bt.logging.warning("Agent output failed schema validation")
                return None

            # Attach audit metadata
            result["_agent_hash"] = agent_hash
            result["_repo_url"] = repo_url
            result["_validated_at"] = datetime.datetime.utcnow().isoformat()

            # Write output
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)

            bt.logging.info(f"Agent output written to {output_file}")
            return result

    except Exception as e:
        bt.logging.warning(f"Failed to run agent from {repo_url}: {e}")
        return None
