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
        for f in confirmed:
            lines.append(f"[CONFIRMED] {f['id']} — Confidence: {f['confidence']*100:.0f}%")
            lines.append(f"  Category: {f['category']}")
            lines.append(f"  {f['description']}")
            lines.append(f"  Artifacts: {', '.join(f['supporting_artifacts'])}")
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
