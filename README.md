# TrafficFlowBench 2026

Course project for **CS501: Practical Applications of Algorithms** using the
[2026 IEEE Big Data Traffic Flow Bench](https://www.kaggle.com/competitions/2026-ieee-big-data-traffic-flow-bench)
competition.

## Team

- Damir Mertl — Data and Integration Lead
- Aayush Agasti — State Reconstruction Lead
- Aliia Rustamova — Queue Prediction Lead
- Viplav Dodeja — Physics Lead
- Meerimgul Abdibaap Kyzy — ODME Lead

## Project goal

Build and evaluate a reproducible traffic-analysis pipeline that reconstructs
missing freeway measurements, forecasts short-term queues, evaluates physical
consistency, and estimates vehicle path flows.

The project addresses all four competition tasks:

1. Reconstruct masked speed and flow measurements.
2. Forecast queued links over the next 30 minutes from permitted history.
3. Assess whether the Task 1 reconstruction respects traffic-flow physics.
4. Estimate nonnegative path flows from link counts, network paths, and priors.

Task 3 has no separate submission rows: the competition evaluates the speed and
flow values submitted for Task 1.

## Project pipeline

The architecture and task relationships are documented in
[docs/architecture.md](docs/architecture.md).

## Repository layout

```text
docs/       Project documentation and architecture
data/       Local competition data (ignored; never commit it)
notebooks/  Exploratory analysis and experiments
src/        Reusable data, modeling, evaluation, and submission code
```

## Data and references

- [Competition page](https://www.kaggle.com/competitions/2026-ieee-big-data-traffic-flow-bench)
- [Official benchmark code, schemas, baselines, and scoring rules](https://github.com/jacky850/trafficflowbench-public)
- [Submitted project proposal](docs/project-proposal.md)

Competition data is downloaded separately from Kaggle. Do not commit downloaded
data, Kaggle credentials, generated submissions, or other large artifacts.
