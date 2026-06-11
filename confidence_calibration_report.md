# Confidence Calibration Report

For each real finding, we show the evolution of confidence over iterations 1-3.

## Confidence Calibration

| Finding ID | Iteration 1 | Iteration 2 | Iteration 3 | Final Confidence |
| :--- | :--- | :--- | :--- | :--- |
| MEM-3908 | 20 | 20 | 20 | 20 |
| MEM-2160 | 20 | 20 | 20 | 20 |
| MAL-924-0x850000 | 30 | 30 | 30 | 35 |
| MAL-948-0x5c0000 | 30 | 30 | 30 | 35 |

## Validation Results

Confidence does not show the expected increase with corroborating evidence, suggesting a calibration issue within the confidence calculation engine when dealing with low-confidence findings. No regression bugs were detected in the engine itself.
