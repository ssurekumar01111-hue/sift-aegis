# Benchmark Validation Report

This report documents the performance of SIFT-AEGIS against the M57 ground truth.

## Metric Definitions

* **True Positives (TP):** Findings that correctly identify ground truth artifacts.
* **False Positives (FP):** Findings that are not in the ground truth.
* **False Negatives (FN):** Ground truth artifacts not identified by the investigation.
* **Precision:** Accuracy of positive identifications (TP / (TP + FP)).
* **Recall:** Ability to find all ground truth artifacts (TP / (TP + FN)).
* **Hallucination Rate:** Proportion of findings that are false positives (FP / Total).

## Benchmark Results

- Total Findings: 12
- True Positives: 0
- False Positives: 12
- False Negatives: 3
- Precision: 0.0
- Recall: 0.0
- Hallucination Rate: 1.0 (100%)

## Validation Status

The investigation results from the current run completely missed the M57 ground truth artifacts and identified entirely different findings, resulting in a 100% hallucination rate when benchmarked against the actual case ground truth.
