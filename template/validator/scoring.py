import json
import bittensor as bt
from typing import Dict, Any, List, Set


def score_with_ground_truth(
    agent_output: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> float:
    """
    Compare agent output against ground truth findings.
    Returns score in [0.0, 1.0]
    
    Scoring Breakdown:
    - 70% F1 Score (precision + recall of findings)
    - 20% Severity Accuracy (correct severity classification)
    - 10% Metadata Quality (files analyzed, timestamps, etc.)
    
    Args:
        agent_output: Agent's output dictionary
        ground_truth: Ground truth dictionary from API
        
    Returns:
        float: Score in [0.0, 1.0]
    """

    # Validate inputs
    if not isinstance(agent_output, dict):
        bt.logging.warning("Agent output is not a dictionary")
        return 0.0
    
    if not isinstance(ground_truth, dict):
        bt.logging.warning("Ground truth is not a dictionary")
        return 0.0

    # Extract findings
    gt_findings = ground_truth.get("findings", [])
    agent_findings = agent_output.get("findings", [])
    
    if not isinstance(gt_findings, list):
        bt.logging.warning("Ground truth findings is not a list")
        return 0.0
    
    if not isinstance(agent_findings, list):
        bt.logging.warning("Agent findings is not a list")
        return 0.0

    # Handle empty ground truth
    if len(gt_findings) == 0:
        if len(agent_findings) == 0:
            bt.logging.info("Both ground truth and agent have no findings - perfect match")
            return 1.0
        else:
            bt.logging.warning("Agent reported findings but ground truth is empty")
            return 0.0

    # Build finding maps by ID or title
    gt_map = {}
    for f in gt_findings:
        finding_id = f.get("id") or f.get("title") or str(len(gt_map))
        gt_map[finding_id] = f

    agent_map = {}
    for f in agent_findings:
        finding_id = f.get("id") or f.get("title") or str(len(agent_map))
        agent_map[finding_id] = f

    if not gt_map:
        bt.logging.warning("No valid findings in ground truth")
        return 0.0

    # Calculate F1 Score
    gt_ids: Set[str] = set(gt_map.keys())
    agent_ids: Set[str] = set(agent_map.keys())
    
    true_positives = len(gt_ids & agent_ids)
    false_positives = len(agent_ids - gt_ids)
    false_negatives = len(gt_ids - agent_ids)
    
    # Calculate precision and recall
    if true_positives + false_positives > 0:
        precision = true_positives / (true_positives + false_positives)
    else:
        precision = 0.0
    
    if true_positives + false_negatives > 0:
        recall = true_positives / (true_positives + false_negatives)
    else:
        recall = 0.0
    
    # Calculate F1
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    bt.logging.debug(
        f"F1 Metrics - TP: {true_positives}, FP: {false_positives}, "
        f"FN: {false_negatives}, Precision: {precision:.3f}, "
        f"Recall: {recall:.3f}, F1: {f1_score:.3f}"
    )

    # Calculate Severity Accuracy
    severity_score = 0.0
    severity_matches = 0
    
    for finding_id in gt_ids & agent_ids:
        gt_finding = gt_map[finding_id]
        agent_finding = agent_map[finding_id]
        
        gt_severity = (gt_finding.get("severity") or "").lower()
        agent_severity = (agent_finding.get("severity") or "").lower()
        
        if gt_severity and agent_severity and gt_severity == agent_severity:
            severity_matches += 1
    
    if true_positives > 0:
        severity_score = severity_matches / true_positives
    
    bt.logging.debug(
        f"Severity - Matches: {severity_matches}/{true_positives}, "
        f"Score: {severity_score:.3f}"
    )

    # Calculate Metadata Quality Score
    metadata_score = 0.0
    metadata_checks = 0
    
    # Check if files_analyzed is reasonable
    if "files_analyzed" in agent_output and "files_analyzed" in ground_truth:
        gt_files = ground_truth.get("files_analyzed")
        agent_files = agent_output.get("files_analyzed")
        
        if isinstance(gt_files, int) and isinstance(agent_files, int):
            if gt_files > 0:
                ratio = agent_files / gt_files
                if 0.5 <= ratio <= 2.0:  # More lenient tolerance
                    metadata_score += 0.5
                metadata_checks += 1
    
    # Check if timestamp exists
    if "timestamp" in agent_output:
        timestamp = agent_output["timestamp"]
        if isinstance(timestamp, str) and len(timestamp) > 0:
            metadata_score += 0.5
            metadata_checks += 1
    
    if metadata_checks > 0:
        metadata_score = metadata_score / metadata_checks
    
    bt.logging.debug(f"Metadata Score: {metadata_score:.3f}")
  
    # Calculate Final Score
    final_score = (
        f1_score * 0.70 +           # 70% weight on F1
        severity_score * 0.20 +      # 20% weight on severity accuracy
        metadata_score * 0.10        # 10% weight on metadata quality
    )
    
    
    final_score = max(0.0, min(1.0, final_score))
   
    bt.logging.info(
        f"Final Score: {final_score:.4f} "
        f"(F1: {f1_score:.3f}, Severity: {severity_score:.3f}, "
        f"Metadata: {metadata_score:.3f})"
    )
    
    return final_score