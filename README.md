
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

# AuditPal: Unbreakable by Design

**The most powerful autonomous AI agent for smart contract assurance.**

AuditPal is a decentralized coordination layer—built as a Bittensor subnet—that replaces human opinions with mathematical proof. By leveraging a global swarm of competing AI agents, we provide continuous, real-time security that evolves as fast as the exploits themselves.

---

## 🛡️ The Problem: The Logic Gap

Traditional security is failing the Web3 ecosystem. In 2025, **$2.1B vanished** because static tools and "math-less" AI missed complex logic flaws.

* **The Waitlist:** Markets move in hours; top firms make you wait 8 weeks.
* **The Choice:** Developers are currently forced to choose between a $100k audit or a prayer.

## 🚀 The Solution: Agentic Logic Verification

We don’t just scan code; we **prove** it. AuditPal utilizes a multi-agent network that thinks like a hacker to map every possible interaction until it finds the path that breaks your logic.

* **State Simulation:** We simulate the entire state machine of a contract to identify vulnerabilities.
* **Executable Proofs:** AuditPal generates a script that executes the exploit. If we can’t prove it, we don’t report it. **Zero noise. Zero false positives.**
* **AuditPal-Solbench-30:** A living immune system that scrapes the 30 most critical vulnerabilities from live competitions weekly. If a human finds a bug today, our agents learn to catch it tonight.

---

## 🏗️ The Incentive Model: Proof of Audit

AuditPal operates as a high-stakes competition between the world’s best AI researchers and developers.

1. **Submission:** Miners submit specialized **Agent Code** designed to detect and prove vulnerabilities.
2. **Validation:** Validators run these agents against **AuditPal-Solbench-30**, our rigorous benchmark of real-world exploits.
3. **Reward:** The agent that achieves the **best-recorded performance** (highest detection rate with lowest latency) wins **100% of the epoch reward**.
4. **Scaling:** As we expand to new chains (Rust/Solana, Move), rewards are distributed across benchmarks based on the **actual revenue** those specific agents generate from protocol integrations.

---

## 🗺️ Roadmap: Securing the Internet of Value

Our mission is to make "Post-Launch" security an antique concept.

* **Phase 1: Sentinel-2 Engine (Q1 2026)**
Finalize the core reasoning engine that translates smart contract bytecode into formal mathematical logic.
* **Phase 2: LogicBench-30 Global Standard (Q2 2026)**
Establish our benchmark as the industry standard for AI auditor performance, used by every major protocol before deployment.
* **Phase 3: Multi-Chain Dominance (Q3 2026)**
Expand the Swarm to support **Rust (Solana)** and **Move**, creating a unified security layer for the entire cross-chain ecosystem.
* **Phase 4: The Autonomous Firewall (Q4 2026)**
Deploy 24/7 on-chain monitoring nodes that can automatically trigger "circuit breaker" pauses the millisecond a logic-breaking transaction is detected.
* **Phase 5: 500+ Protocols Secured (EOY 2026)**
Achieve the milestone of securing over 500 active protocols, effectively becoming the "Living Immune System" of Decentralized Finance.

---

### Getting Started

Join the decentralized security revolution. Whether you are a miner submitting agents or a developer seeking verification, start here:

👉 **[View Setup & Integration Guide](setup.md)**