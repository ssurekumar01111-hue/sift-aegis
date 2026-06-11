# Attack Chain Validation

This report documents the attack chain reconstructed from real M57 findings and the confidence calculations.

## Attack Chain Confidence Formula

The Attack Chain Confidence is calculated as the average confidence score of all nodes in the evidence graph:

Formula: `Confidence = (Σ Confidence of all nodes) / (Total Number of Nodes)`

Based on the evidence graph generated, the calculated confidence is: 0.7419 (or 74.19%).

## Contribution of Key Findings

### MEM-3908 (Suspicious Process: cmd.exe)
* Confidence: 0.25
* Role: Identified as an early-stage indicator of anomalous parent-child process relationship. It provides initial context but has low confidence, requiring further corroboration.

### MEM-2160 (Suspicious Process: mdd_1.3.exe)
* Confidence: 0.25
* Role: Similar to MEM-3908, it acts as a low-confidence indicator of anomalous process activity.

Both findings contribute to the overall graph's body of evidence but, being unverified and having low individual confidence, they act as supporting nodes rather than primary drivers of the attack chain's overall confidence.
