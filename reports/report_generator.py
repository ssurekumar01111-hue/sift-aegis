#!/usr/bin/env python3
"""
SIFT-AEGIS DFIR Report Generator
Converts investigation results into human-readable narrative report.
"""

import json
from datetime import datetime

def generate_report(results_path: str, output_path: str):
    with open(results_path) as f:
        results = json.load(f)
    
    findings = results["findings"]
    summary = results["summary"]
    tool_calls = results["tool_calls"]
    
    confirmed = [f for f in findings if f["status"] == "CONFIRMED"]
    inferred = [f for f in findings if f["status"] == "INFERRED"]
    unverified = [f for f in findings if f["status"] == "UNVERIFIED"]
    rejected = [f for f in findings if f["status"] == "REJECTED"]
    
    lines = []
    lines.append("="*70)
    lines.append("SIFT-AEGIS AUTONOMOUS DFIR INVESTIGATION REPORT")
    lines.append("="*70)
    lines.append(f"Generated: {datetime.utcnow().isoformat()} UTC")
    lines.append(f"Evidence: charlie-2009-12-11 (M57-Patents Scenario)")
    lines.append(f"Framework: SIFT-AEGIS + OpenClaw + Gemini 3.1 Flash-Lite")
    lines.append("")
    
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-"*40)
    lines.append(f"Total Findings:     {summary['total_findings']}")
    lines.append(f"Confirmed:          {summary['confirmed']}")
    lines.append(f"Inferred:           {summary['inferred']}")
    lines.append(f"Unverified:         {summary['unverified']}")
    lines.append(f"Rejected:           {summary['rejected']}")
    lines.append(f"Self-Corrections:   {summary['corrections_made']}")
    lines.append(f"Tool Calls:         {summary['total_tool_calls']}")
    lines.append(f"Iterations Run:     {summary['iterations_run']}")
    lines.append("")
    
    if confirmed:
        lines.append("CONFIRMED FINDINGS")
        lines.append("-"*40)
        for i, f in enumerate(confirmed, 1):
            lines.append(f"[{i}] [{f['status']}] {f['id']}")
            lines.append(f"    Confidence:  {f['confidence']*100:.0f}%")
            lines.append(f"    Category:    {f['category']}")
            lines.append(f"    Description: {f['description']}")
            lines.append(f"    Artifacts:   {len(f['supporting_artifacts'])} sources")
            for artifact in f['supporting_artifacts']:
                lines.append(f"      → {artifact}")
            if f.get('contradictions'):
                lines.append(f"    Contradictions checked: {', '.join(f['contradictions'])}")
            lines.append(f"    Detected in: Iteration {f['iteration_found']}")
            lines.append(f"    Source tool: {f['tool_source']}")
            lines.append("")
    
    if inferred:
        lines.append("INFERRED FINDINGS")
        lines.append("-"*40)
        for f in inferred:
            lines.append(f"[INFERRED] {f['id']} — Confidence: {f['confidence']*100:.0f}%")
            lines.append(f"  Category: {f['category']}")
            lines.append(f"  {f['description']}")
            lines.append("")
    
    if rejected:
        lines.append("REJECTED CLAIMS (Hallucination Prevention)")
        lines.append("-"*40)
        for f in rejected:
            lines.append(f"[REJECTED] {f['id']}")
            lines.append(f"  {f['description']}")
            lines.append(f"  Reason: {', '.join(f['contradictions'])}")
            lines.append("")
    
    lines.append("AUDIT TRAIL (Tool Execution Chain)")
    lines.append("-"*40)
    for call in tool_calls:
        lines.append(
            f"[{call['timestamp']}] iter={call['iteration']} "
            f"tool={call['tool']} "
            f"results={call['result_summary']}"
        )
    lines.append("")

    # Accuracy benchmark section
    accuracy_delta = results.get("accuracy_delta", {})
    if accuracy_delta:
        lines.append("ACCURACY BENCHMARK (M57-Patents Ground Truth)")
        lines.append("-"*40)
        lines.append(f"Iteration 1 accuracy:  {accuracy_delta.get('iteration_1_accuracy', 0)*100:.0f}%")
        lines.append(f"Final accuracy:        {accuracy_delta.get('final_accuracy', 0)*100:.0f}%")
        lines.append(f"Improvement:           +{accuracy_delta.get('improvement', 0)}%")
        lines.append("")
        lines.append("Per-iteration breakdown:")
        for iter_data in accuracy_delta.get("iterations", []):
            lines.append(
                f"  Iteration {iter_data['iteration']}: "
                f"total={iter_data['total']} "
                f"confirmed={iter_data['confirmed']} "
                f"unverified={iter_data['unverified']} "
                f"accuracy={iter_data['accuracy_score']*100:.0f}%"
            )
        lines.append("")
    
    # Analyst reasoning section  
    lines.append("ANALYST REASONING CHAIN")
    lines.append("-"*40)
    reasoning_events = [
        e for e in results.get("audit_log", [])
        if e.get("event") == "ANALYST_REASONING"
    ]
    for r in reasoning_events:
        d = r.get("data", {})
        lines.append(f"[{r['timestamp']}] Step: {d.get('step', '')}")
        lines.append(f"  Reasoning: {d.get('reasoning', '')}")
        lines.append(f"  Tool chosen: {d.get('tool_chosen', '')}")
        lines.append(f"  Expected: {d.get('expected', '')}")
        lines.append(f"  Looking for: {d.get('looking_for', '')}")
        lines.append("")
    
    # Multi-source correlation section
    lines.append("MULTI-SOURCE CORRELATION SUMMARY")
    lines.append("-"*40)
    disk_events = [
        e for e in results.get("audit_log", [])
        if e.get("event") in ["MULTI_SOURCE_CONFIRMED", "DISK_CORRELATION_RESULT"]
    ]
    if disk_events:
        for e in disk_events:
            d = e.get("data", {})
            if e["event"] == "MULTI_SOURCE_CONFIRMED":
                lines.append(
                    f"  CROSS-SOURCE MATCH: {d.get('finding_id')} "
                    f"confirmed by disk artifact {d.get('disk_artifact')} "
                    f"AND memory artifact {d.get('memory_artifact')}"
                )
            else:
                lines.append(f"  {d.get('result', '')} — {d.get('note', '')}")
    else:
        lines.append("  No disk-memory contradictions found.")
    lines.append("")
    
    lines.append("="*70)
    lines.append("END OF REPORT")
    lines.append("="*70)
    
    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)
    
    print(report)
    return report

if __name__ == "__main__":
    generate_report(
        "/home/sansforensics/sift-aegis/investigation_results.json",
        "/home/sansforensics/sift-aegis/reports/dfir_report.txt"
    )
