# Real Benchmark Results

## Metric Calculation

- **Total Ground Truth Entries:** 10
- **TP (True Positives):** 0
- **FP (False Positives):** 11 (Agent findings regarding memory processes and injection are completely irrelevant to the forensic scenario described by the real artifacts. They lack support from real browser, email, or document artifacts.)
- **FN (False Negatives):** 10 (Agent failed to detect all 10 ground truth events.)

### Formulas
- **Precision:** TP / (TP + FP) = 0 / (0 + 11) = 0.0
- **Recall:** TP / (TP + FN) = 0 / (0 + 10) = 0.0
- **F1:** 2 * (Precision * Recall) / (Precision + Recall) = 0.0
- **Hallucination Rate:** FP / (TP + FP) = 11 / (0 + 11) = 1.0
- **Inference Accuracy:** TP / total GT entries = 0 / 10 = 0.0

## Summary
The agent currently performs zero detection of the actual M57 forensic events and produces a high volume of irrelevant findings from memory analysis, resulting in an F1 score of 0.0 and a 100% hallucination rate relative to the ground truth.
