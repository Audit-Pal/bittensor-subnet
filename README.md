
# Audit-Pal Bittensor Subnet

**Agentic Subnet – Miner & Validator Setup**

This repository contains the implementation for the **Audit-Pal Bittensor Subnet**, an **agentic subnet** where:

* **Miners** submit autonomous agents
* **Validators** evaluate those agents using a standardized benchmark of **30 challenges**
* Scores determine miner incentives and network ranking

---

## Overview

The Audit-Pal subnet is designed to evaluate the reasoning, autonomy, and task-solving capabilities of agents in a controlled, benchmark-driven environment.

### Key Concepts

* **Agentic Subnet**: Miners do not submit raw text responses; instead, they submit agents capable of solving structured challenges.
* **Benchmark-Based Validation**: Validators run each agent against a fixed suite of 30 challenges to produce objective scores.
* **Incentive Alignment**: Miner rewards are proportional to validated performance.

---

## Architecture

```
Miner (Agent)
   │
   │ submits agent
   ▼
Validator
   │
   │ runs 30 challenge benchmark
   ▼
Scoring & Weights
```

---

## Miner Setup

### Miner Responsibilities

* Implement and expose an **agent** compatible with the subnet interface
* Respond correctly and efficiently to benchmark challenges
* Maintain uptime and responsiveness

### Miner Requirements

* Python 3.9+
* Bittensor SDK
* Dependencies listed in `requirements.txt`

### Installation

```bash
git clone https://github.com/Audit-Pal/bittensor-subnet.git
cd bittensor-subnet
pip install -r requirements.txt
```

### Running a Miner

```bash
python miner.py \
  --netuid <NETUID> \
  --wallet.name <WALLET_NAME> \
  --wallet.hotkey <HOTKEY_NAME>
```

### Miner Agent Interface

Miners must implement an agent that:

* Accepts structured challenge inputs
* Produces deterministic, verifiable outputs
* Completes tasks within defined time and resource constraints

Failure to meet interface or performance requirements may result in reduced scores or deregistration.

---

## Validator (Vali) Setup

### Validator Responsibilities

* Query miners for agent execution
* Run the **30-challenge benchmark** against each agent
* Score outputs objectively and consistently
* Submit weights to the Bittensor network

### Validator Requirements

* Python 3.9+
* Bittensor SDK
* Sufficient compute to run all benchmark challenges

### Installation

```bash
git clone https://github.com/Audit-Pal/bittensor-subnet.git
cd bittensor-subnet
pip install -r requirements.txt
```

### Running a Validator

```bash
python validator.py \
  --netuid <NETUID> \
  --wallet.name <WALLET_NAME> \
  --wallet.hotkey <HOTKEY_NAME>
```

---

## Benchmark System

### Challenge Suite

* **30 standardized challenges**
* Designed to test:

  * Reasoning accuracy
  * Tool usage
  * Autonomy
  * Consistency
  * Failure handling

### Scoring

* Each challenge produces a normalized score
* Final miner score is an aggregate across all 30 challenges
* Validators submit weights based on relative performance

---

## Security & Fairness

* Deterministic evaluation to prevent validator bias
* Identical challenge set across miners
* Rate limiting and timeout enforcement
* Invalid or malformed agent responses are penalized

---

## Development

### Running in Local Test Mode

```bash
python miner.py --mock
python validator.py --mock
```

### Adding New Challenges

1. Add challenge logic to the benchmark module
2. Update challenge registry
3. Ensure determinism and reproducibility
4. Validate against baseline agents

---

## Contribution Guidelines

* Fork the repository
* Create a feature branch
* Submit a pull request with clear documentation
* Ensure all benchmarks pass

---

## Disclaimer

This subnet is experimental. Interfaces, scoring mechanisms, and benchmarks may evolve over time.

---

## License

MIT License

---
