import numpy as np
from typing import List, Optional
import bittensor as bt
from template.protocol import Dummy
from template.validator.agent_runner import wrun_github_agent

def reward(response: Optional[Dummy]) -> float:
    """
    Reward a miner based on whether it returned a valid github_url.
    """

    if response is None:
        bt.logging.info("Reward: response is None")
        return 0.0
    agent = wrun_github_agent(response, "task.json", "output.json")
    
    with open("ground_truth.json", "r") as f:
        ground_truth = f.read()
    
    with open("output.json", "r") as f:
        task_data = f.read()
    

    if agent and task_data in ground_truth:
        bt.logging.info(f"Reward: valid agent received: {agent}")
        return 1.0

    bt.logging.info(f"Reward: Task data not found in agent: {agent}")
    return 0.0


def get_rewards(
    self,
    responses: List[Optional[Dummy]],
) -> np.ndarray:
    """
    Compute rewards for all miner responses.
    """
    return np.array([reward(response) for response in responses], dtype=np.float32)
