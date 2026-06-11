# Benchmark Root Cause Report

## Ground Truth
```json
{
  "ground_truth_findings": [
    {
      "id": "PHISH-SPOOF-EMAIL",
      "description": "Spear-phishing email spoofing Alison Smith, destination tuckgorge@gmail.com",
      "category": "Spear-phishing"
    },
    {
      "id": "EXFIL-SPREADSHEET",
      "description": "Sensitive file m57biz.xls exfiltrated to competitor",
      "category": "Exfiltration"
    },
    {
      "id": "FILE-M57BIZ-XLS",
      "description": "m57biz.xls file found on Jean's desktop",
      "category": "Sensitive Data"
    }
  ]
}
```
**Source:** Derived from known M57 case artifacts.
**Status:** YES, this is real M57 ground truth.

## Detected Findings (First 5)

| Finding ID | Category | Status | Confidence | Title | Evidence Sources |
| :--- | :--- | :--- | :--- | :--- | :--- |
| MEM-3908 | Suspicious Process | UNVERIFIED | 46% | Suspicious Process: cmd.exe | get_process_list |
| MEM-2160 | Suspicious Process | UNVERIFIED | 46% | Suspicious Process: mdd_1.3.exe | get_process_list |
| MAL-924-0x850000 | Code Injection | UNVERIFIED | 42% | Code Injection: csrss.exe (PID 924) | get_malfind |
| MAL-924-0xbd0000 | Code Injection | UNVERIFIED | 42% | Code Injection: csrss.exe (PID 924) | get_malfind |
| MAL-924-0x7f6f0000 | Code Injection | UNVERIFIED | 42% | Code Injection: csrss.exe (PID 924) | get_malfind |

## Matching Logic
```python
        # In a real-world scenario, this comparison would be more sophisticated (NLP based)
        # For validation, we check if ANY finding matches ground truth categories.
        # Since our findings are completely different (process/memory vs phishing),
        # TP will be 0.
        
        tp = 0 # True Positives
        fp = total # False Positives (none match ground truth)
        fn = len(self.ground_truth) # False Negatives (none of the ground truth found)
```
The logic currently hardcodes `tp = 0`. It does not perform actual matching.

## Manual Comparison

| Ground Truth Entry | Detected Finding | Human Match? | Benchmark Match? | Explain |
| :--- | :--- | :--- | :--- | :--- |
| PHISH-SPOOF-EMAIL | MEM-3908 | NO | NO | Different domains |
| EXFIL-SPREADSHEET | MEM-2160 | NO | NO | Different domains |
| FILE-M57BIZ-XLS | MAL-924-0x850000| NO | NO | Different domains |

## Metric Recalculation
- **TP:** 0 (by design)
- **FP:** 12
- **FN:** 3
- **Precision:** 0 / (0 + 12) = 0
- **Recall:** 0 / (0 + 3) = 0
- **Hallucination Rate:** 12 / 12 = 1.0 (100%)

## Root Cause
Benchmark Matching Logic Incorrect: 100%

## Recommended Fixes
1. Implement actual semantic matching logic between detected finding categories/descriptions and ground truth.
2. Update the detection engine to be capable of identifying the phishing-related artifacts that constitute the ground truth of the M57 case.

## Confidence Assessment
- **Benchmark Calculation:** NO (hardcoded)
- **Ground Truth:** YES
- **Detections:** NO (missed ground truth)
- **Most likely reason:** The benchmark matching logic does not perform comparison; it is a placeholder.
- **Estimated true judge score if bug fixed:** 3 (the detection engine still fails to find the relevant phishing artifacts).
