# Phase 2.5 — Confidence Calibration & Corroboration Engine Report

## Current Confidence Audit
The original confidence formula was:
`Score = Sum(source_weights) + (0.05 * supporting_evidence_count) - (0.25 * contradictory_evidence_count) - (0.10 * missing_evidence_count) - (0.15 if "missing_verification")`
This model relied heavily on presence/absence of evidence and penalized missing evidence heavily, which led to low confidence (20%) even when findings were detected. It lacked nuanced understanding of corroboration or hypothesis alignment.

## New Confidence Formula
`Score = Sum(Weights) + (0.05 * SupportingCount) + CorroborationBonus + HypothesisBonus - (0.25 * ContradictionCount) - (0.03 * MissingCount)`

## Weight Changes
- Missing Evidence Impact: Reduced from -0.10 to -0.03 per item.
- Corroboration and Hypothesis bonuses added as new additive components.

## Corroboration Engine Design
Bonuses applied for combinations of independent sources to reward corroboration:
- Process + DLL: +0.10
- Process + DLL + Network: +0.20
- Process + Registry + MFT + Network: +0.30

## Hypothesis Alignment Design
Bonus: +0.10 if `evidence_sources` match requirement defined for finding `category`.

## Files Modified
- `orchestrator.py`: Updated `calculate_confidence` and added `_get_corroboration_bonus`, `_get_hypothesis_bonus`.
- `test_confidence_engine.py`: Added to validate the new formula.

## Confidence History Enhancements
Added `confidence_history` to `Finding` model to track updates, and integrated `self.log` calls in `calculate_confidence` for `CONFIDENCE_RECALCULATED` and `CONFIDENCE_EVOLUTION`.

## Sample Finding Before
Confidence: 20%
Reasoning: "1 pieces of supporting evidence identified. Additional evidence required..."

## Sample Finding After (Validated)
Confidence: 80% (for the test finding)
Reasoning: Recalculated with Corroboration and Hypothesis bonuses applied.

## Confidence Evolution Examples
`{"finding_id": "TEST-1", "old_confidence": 0.0, "new_confidence": 0.8, "reason": "Recalculated: Base + 0.2 (corroboration) + 0.1 (hypothesis)", "timestamp": "..."}`

## Audit Trail Examples
`[2026-06-11T16:15:40.426054] [CORROBORATION_BONUS_APPLIED] {"finding_id": "TEST-1", "bonus": 0.2}`
`[2026-06-11T16:15:40.426146] [HYPOTHESIS_ALIGNMENT_BONUS_APPLIED] {"finding_id": "TEST-1", "bonus": 0.1}`

## Validation Results
The test finding "TEST-1" achieved the expected confidence of 0.8 based on the new formula, confirming that corroboration and hypothesis alignment bonuses correctly increase confidence.

## PHASE 2.5 STATUS
* Completed: YES
* Confidence Recalibrated: YES
* Corroboration Engine Implemented: YES
* Hypothesis Alignment Implemented: YES
* Confidence Evolution Tracking Implemented: YES
* Validation Completed: YES
