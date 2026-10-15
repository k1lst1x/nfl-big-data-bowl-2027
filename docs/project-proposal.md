# Project Proposal NFL Combine Traits and Yards After Catch

**Course:** CS501: Practical Applications of Algorithms

**Team:** Damir Mertl, Aayush Agasti, Aliia Rustamova, Viplav Dodeja, Meerimgul Abdibaap Kyzy

**Competition:** [NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/overview)

## Purpose

We will investigate which athletic traits measured at the NFL Scouting Combine
are associated with yards after catch (YAC) among NFL wide receivers. By
comparing traditional Combine results with movement features derived from
tracking data, we will evaluate whether pre-draft speed, acceleration, and
change of direction translate into receiving performance after the catch.

The main goal is to identify and explain patterns. Predictive modeling will
support the analysis only where the sample permits reliable validation.

## Scope and research question

The primary population is wide receivers represented in the 2023–2025 Combine
and NFL game datasets. We will inspect player overlap, drill coverage, receiving
plays, tracking units, and available outcome fields before fixing the analytical
sample. Tight ends may be considered only as a separate extension if data
coverage permits.

The primary outcome is observed YAC per reception over a documented NFL game
sample. We will validate the supplied `yards_after_catch` field and document the
handling of receptions, missing outcomes, repeated drill attempts, and receiving
context.

> Which athletic traits measured at the NFL Combine translate into better YAC
> performance among wide receivers, and do tracking-derived traits add
> information beyond traditional Combine measurements?

Results will describe associations, not causal effects or guaranteed scouting
accuracy.

## Team roles

| Member | Role | Responsibilities |
| --- | --- | --- |
| Damir | Data and Integration Lead | Data loading, cleaning, joins, shared utilities, reproducibility, and final notebook integration |
| Aayush | Combine Feature Engineering Lead | Traditional measurements, receiver-drill segmentation, and baseline athletic features |
| Aliia | NFL Performance and Outcome Lead | YAC per reception, reception counts, observation window, and receiving context |
| Viplav | Movement Physics Lead | Tracking units, speed, acceleration, deceleration, directional change, and path-efficiency measures |
| Meerimgul | Modeling and Validation Lead | Associations, interpretable models, player-grouped validation, uncertainty, and feature-set comparisons |

## Work plan

| Sprint | Milestone | Deliverable |
| --- | --- | --- |
| 1 — Understand | Inventory and connect the competition data | Dataset overview, initial tracking visualizations, proposed YAC definition, and approved research question |
| 2 — Baseline | Working first version of every analytical component | Joined player table, YAC outcome, initial motion features, and baseline associations |
| 3 — Improve | Determine whether tracking adds signal beyond traditional measures | Refined features, context checks, model comparison, and experiment log |
| 4 — Connect | Integrate movement, opportunity, and football interpretation | End-to-end reproducible analysis and interpretable effects |
| 5 — Evaluate | Produce the strongest defensible candidate | Error, ablation, sensitivity, and limitation analysis |
| 6 — Finalize | Complete competition and class deliverables | Public notebook, competition writeup, final report, presentation, and frozen code |

The team begins with interpretable baselines, applies regularized or simple
regression first, and tests more complex models only when sample size and
validation justify them.

## Expected outcome

The project will deliver a reproducible analysis explaining whether and how
traditional Combine results and tracking-derived athletic traits are associated
with YAC per reception. Deliverables include documented code, a public Kaggle
notebook, clear visualizations, a concise competition writeup, a class report,
and a presentation. A weak or absent relationship is a valid result when
supported by the data.
