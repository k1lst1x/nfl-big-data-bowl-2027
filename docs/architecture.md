# Traffic-analysis pipeline

This diagram shows how the four competition tasks fit together. It deliberately
describes the project at a high level; model choices will be evaluated and
recorded during the project sprints.

```mermaid
flowchart TD
    D[Competition data\nstate observations, network, ramps, counts, paths]

    D --> T1[Task 1\nReconstruct masked speed and flow]
    T1 --> T3[Task 3\nEvaluate physics consistency\nfundamental diagram and conservation]

    D --> T2[Task 2\nForecast queues\n60-minute history → 30-minute horizon]
    D --> T4[Task 4\nEstimate nonnegative path flows\ncounts + incidence matrix + prior]

    T1 --> S[Unified Kaggle submission CSV]
    T2 --> S
    T4 --> S

    T3 -. scores the Task 1 values; no separate upload .-> S
```

## Interpretation

- **Task 1** produces reconstructed speed and flow values for masked state rows.
- **Task 3** evaluates those same Task 1 values for fundamental-diagram validity
  and vehicle conservation; it does not require a separate prediction file.
- **Task 2** is an online forecasting task: each window supplies 60 minutes of
  history and requires queue predictions for the next 30 minutes.
- **Task 4** is a separate origin-destination/path-flow estimation problem based
  on released link counts, paths, an incidence matrix, and a prior.
- The final upload combines Task 1, Task 2, and Task 4 rows into one CSV.
