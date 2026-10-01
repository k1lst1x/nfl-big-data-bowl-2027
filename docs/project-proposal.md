# Project Proposal

**Course:** CS501: Practical Applications of Algorithms
**Team:** Damir Mertl, Aayush Agasti, Aliia Rustamova, Viplav Dodeja, Meerimgul Abdibaap Kyzy

**Project:** [2026 IEEE Big Data Traffic Flow Bench](https://www.kaggle.com/competitions/2026-ieee-big-data-traffic-flow-bench/overview)
**Repository:** [k1lst1x/trafficflowbench-2026](https://github.com/k1lst1x/trafficflowbench-2026)

## Introduction

This project develops a traffic-analysis pipeline using the dataset provided by
the 2026 IEEE Big Data Traffic Flow Benchmark competition. The work addresses
missing speed and flow measurements, short-term queue forecasting, physical
consistency of reconstructed traffic states, and estimation of vehicle path
flows.

The scope is limited to offline analysis and evaluation of the supplied dataset.
Deployment to a real traffic-management system is outside the project.

## Objectives

The primary objective is to build and evaluate a reproducible pipeline that
reconstructs incomplete traffic data, forecasts congestion, and estimates path
flows while considering traffic-flow constraints.

Supporting objectives are to compare simple baselines with improved methods,
identify conditions where predictions perform poorly, and investigate the
tradeoff between prediction accuracy and physical consistency.

## Team responsibilities

| Member | Role | Responsibilities |
| --- | --- | --- |
| Damir | Data / Integration Lead | Data loading, preprocessing, shared utilities, validation, experiment tracking, and submission pipeline |
| Aayush | State Reconstruction Lead | Task 1: reconstruct missing speed and flow readings |
| Aliia | Queue Prediction Lead | Task 2: forecast queues using permitted traffic history |
| Viplav | Physics Lead | Task 3 and Task 1 support: evaluate physical consistency and traffic-aware corrections |
| Meerimgul | ODME Lead | Task 4: estimate nonnegative path flows from counts, paths, incidence matrices, and priors |

Task 3 evaluates the states reconstructed for Task 1; it does not require a
separate prediction model or upload.

## Work plan

| Sprint | Milestone | Main deliverable |
| --- | --- | --- |
| 1 — Understand | Load, explore, visualize, and submit the data | Dataset inventory, initial visualizations, and valid dummy submission |
| 2 — Baseline | Every prediction component has a working solution | Baseline v1 with component evaluations |
| 3 — Improve | Demonstrate measurable improvement over baseline | Model v2 and experiment log |
| 4 — Integrate | Integrate traffic-aware improvements | Integrated candidate and documented interfaces |
| 5 — Optimize | Produce the strongest validated candidate | Submission Candidate v1 and ablation analysis |
| 6 — Finalize | Complete submission and class deliverables | Reproducible code, final report, and presentation |

The team will begin with interpretable baselines, then test machine-learning and
optimization methods only where validation supports the added complexity. Work
will use shared reviews and rotating paired collaboration to balance the
workload and support learning.

## Expected outcome

The expected outcome is a working pipeline that produces the required traffic
predictions and assembles them into the competition submission format. Final
deliverables will include documented source code, reproducible experiments,
traffic visualizations, a report, and a presentation. Success is measured by a
complete, reproducible implementation, sound evaluation, and demonstrated team
learning; improvement over baseline methods is a target rather than a guarantee.
