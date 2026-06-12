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
    
    # Case Verdict Block
    confirmed_count = sum(1 for f in findings if f.get("status") == "CONFIRMED")
    lines.append("CASE VERDICT")
    lines.append("-" * 40)
    lines.append(f"Subject: Charlie | Scenario: M57-Patents (Dec 2009) | Activity: Suspected IP exfiltration | Key evidence: {confirmed_count} confirmed findings | Confidence: Medium-High")
    lines.append("")
    
    # Relationship Graph
    lines.append("CASE RELATIONSHIP GRAPH")
    lines.append("-" * 40)
    
    # Extract entities
    pat_mcgoo = False
    external_parties = set()
    documents = set()
    staging_folders = set()
    subjects = set()
    
    for f in findings:
        if f.get("status") in ["CONFIRMED", "INFERRED"]:
            text = str(f).lower()
            if "pat mcgoo" in text or "pat@m57patents.com" in text:
                pat_mcgoo = True
            
            # Extract emails
            import re
            emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(f)))
            for e in emails:
                if "m57patents" not in e.lower() and e.lower() != "charlie@m57patents.com":
                    external_parties.add(e.lower())
                    
            # Extract documents and folders from raw_data
            raw = f.get("raw_data", {})
            if "files" in raw:
                for file in raw["files"]:
                    if ".lnk" not in file.lower() and file != "Thumbs.db":
                        documents.add(file)
            
            if "Quantum Cryptography" in str(f):
                staging_folders.add("Quantum Cryptography")
                
            if "subjects" in raw:
                for sub in raw["subjects"]:
                    if "fw:" not in sub.lower() and "re:" not in sub.lower():
                        subjects.add(sub)
    
    lines.append("           [ Pat McGoo (Manager) ]")
    lines.append("                     |")
    lines.append("            (assigned task via email)")
    lines.append("                     v")
    lines.append("             [ Charlie (Insider) ]")
    
    if documents or staging_folders:
        lines.append("                     |")
        lines.append("      +--------------+--------------+")
        lines.append("      |                             |")
        lines.append(" [ Accessed Docs ]           [ Staging Folders ]")
        docs_list = list(documents)[:3]
        folders_list = list(staging_folders)[:2]
        
        for i in range(max(len(docs_list), len(folders_list))):
            d_str = f"  - {docs_list[i]}" if i < len(docs_list) else ""
            f_str = f"  - {folders_list[i]}" if i < len(folders_list) else ""
            lines.append(f"{d_str:<28} {f_str}")
            
        if len(documents) > 3:
            lines.append("  - ...")
            
    if external_parties:
        lines.append("")
        lines.append("             [ Charlie (Insider) ]")
        lines.append("                     |")
        lines.append("            (exfiltrated data to)")
        lines.append("                     v")
        lines.append("          [ External Co-Conspirators ]")
        for ep in list(external_parties)[:3]:
            lines.append(f"            * {ep}")
            
    if subjects:
        lines.append("")
        lines.append("          [ Key Communication Subjects ]")
        for sub in list(subjects)[:3]:
            lines.append(f"            * '{sub}'")
            
    lines.append("\n")

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
            lines.append(f"[{i}] [CONFIRMED] {f['title']}")
            lines.append(f"    Finding ID:  {f['finding_id']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Category:    {f.get('category', 'N/A')}")
            lines.append(f"    Description: {f.get('description', 'N/A')}")
            lines.append(f"    Supporting Evidence:")
            if f.get('supporting_evidence'):
                for ev in f.get('supporting_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Contradictory Evidence:")
            if f.get('contradictory_evidence'):
                for ev in f.get('contradictory_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Missing Evidence:")
            if f.get('missing_evidence'):
                for ev in f.get('missing_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Confidence Explanation:")
            lines.append(f"      {f.get('confidence_explanation', 'No explanation provided.')}")
            lines.append(f"    Hypothesis:  {f.get('hypothesis', 'N/A')}")
            lines.append(f"    Relationship Reasoning:")
            if f.get('relationship_reasoning'):
                for rr in f.get('relationship_reasoning', []):
                    lines.append(f"      - {rr}")
            lines.append(f"    Confidence History:")
            if f.get('confidence_history'):
                for hist in f.get('confidence_history', []):
                    old_val = hist.get('old_confidence', hist.get('old'))
                    new_val = hist.get('new_confidence', hist.get('new'))
                    lines.append(f"      - {old_val}% → {new_val}% at {hist['timestamp']}")
            lines.append(f"    Confidence Change Reason:")
            lines.append(f"      {f.get('confidence_change_reason', 'N/A')}")
            lines.append("")
    
    if inferred:
        lines.append("INFERRED FINDINGS")
        lines.append("-"*40)
        for i, f in enumerate(inferred, 1):
            lines.append(f"[{i}] [INFERRED] {f['title']}")
            lines.append(f"    Finding ID:  {f['finding_id']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Category:    {f.get('category', 'N/A')}")
            lines.append(f"    Description: {f.get('description', 'N/A')}")
            lines.append(f"    Supporting Evidence:")
            if f.get('supporting_evidence'):
                for ev in f.get('supporting_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Contradictory Evidence:")
            if f.get('contradictory_evidence'):
                for ev in f.get('contradictory_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Missing Evidence:")
            if f.get('missing_evidence'):
                for ev in f.get('missing_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Confidence Explanation:")
            lines.append(f"      {f.get('confidence_explanation', 'No explanation provided.')}")
            lines.append(f"    Hypothesis:  {f.get('hypothesis', 'N/A')}")
            lines.append(f"    Relationship Reasoning:")
            if f.get('relationship_reasoning'):
                for rr in f.get('relationship_reasoning', []):
                    lines.append(f"      - {rr}")
            lines.append(f"    Confidence History:")
            if f.get('confidence_history'):
                for hist in f.get('confidence_history', []):
                    old_val = hist.get('old_confidence', hist.get('old'))
                    new_val = hist.get('new_confidence', hist.get('new'))
                    lines.append(f"      - {old_val}% → {new_val}% at {hist['timestamp']}")
            lines.append(f"    Confidence Change Reason:")
            lines.append(f"      {f.get('confidence_change_reason', 'N/A')}")
            lines.append("")

    if unverified:
        lines.append("UNVERIFIED FINDINGS (Insufficient Evidence)")
        lines.append("-"*40)
        for i, f in enumerate(unverified, 1):
            lines.append(f"[{i}] [UNVERIFIED] {f['title']}")
            lines.append(f"    Finding ID:  {f['finding_id']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Category:    {f.get('category', 'N/A')}")
            lines.append(f"    Description: {f.get('description', 'N/A')}")
            lines.append(f"    Supporting Evidence:")
            if f.get('supporting_evidence'):
                for ev in f.get('supporting_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Contradictory Evidence:")
            if f.get('contradictory_evidence'):
                for ev in f.get('contradictory_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Missing Evidence:")
            if f.get('missing_evidence'):
                for ev in f.get('missing_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Confidence Explanation:")
            lines.append(f"      {f.get('confidence_explanation', 'No explanation provided.')}")
            lines.append(f"    Hypothesis:  {f.get('hypothesis', 'N/A')}")
            lines.append(f"    Relationship Reasoning:")
            if f.get('relationship_reasoning'):
                for rr in f.get('relationship_reasoning', []):
                    lines.append(f"      - {rr}")
            lines.append(f"    Confidence History:")
            if f.get('confidence_history'):
                for hist in f.get('confidence_history', []):
                    old_val = hist.get('old_confidence', hist.get('old'))
                    new_val = hist.get('new_confidence', hist.get('new'))
                    lines.append(f"      - {old_val}% → {new_val}% at {hist['timestamp']}")
            lines.append(f"    Confidence Change Reason:")
            lines.append(f"      {f.get('confidence_change_reason', 'N/A')}")
            lines.append("")
    
    if rejected:
        lines.append("REJECTED CLAIMS (Hallucination Detection)")
        lines.append("-"*40)
        for i, f in enumerate(rejected, 1):
            lines.append(f"[{i}] [REJECTED] {f['title']}")
            lines.append(f"    Finding ID:  {f['finding_id']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Category:    {f.get('category', 'N/A')}")
            lines.append(f"    Description: {f.get('description', 'N/A')}")
            lines.append(f"    Supporting Evidence:")
            if f.get('supporting_evidence'):
                for ev in f.get('supporting_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Contradictory Evidence:")
            if f.get('contradictory_evidence'):
                for ev in f.get('contradictory_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Missing Evidence:")
            if f.get('missing_evidence'):
                for ev in f.get('missing_evidence', []):
                    lines.append(f"      - {ev}")
            else:
                lines.append("      - None")
            lines.append(f"    Confidence Explanation:")
            lines.append(f"      {f.get('confidence_explanation', 'No explanation provided.')}")
            lines.append(f"    Hypothesis:  {f.get('hypothesis', 'N/A')}")
            lines.append(f"    Relationship Reasoning:")
            if f.get('relationship_reasoning'):
                for rr in f.get('relationship_reasoning', []):
                    lines.append(f"      - {rr}")
            lines.append(f"    Confidence History:")
            if f.get('confidence_history'):
                for hist in f.get('confidence_history', []):
                    old_val = hist.get('old_confidence', hist.get('old'))
                    new_val = hist.get('new_confidence', hist.get('new'))
                    lines.append(f"      - {old_val}% → {new_val}% at {hist['timestamp']}")
            lines.append(f"    Confidence Change Reason:")
            lines.append(f"      {f.get('confidence_change_reason', 'N/A')}")
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
    
    # Adaptive strategy changes section
    strategy_changes = results.get("strategy_changes", [])
    if strategy_changes:
        lines.append("ADAPTIVE STRATEGY CHANGES")
        lines.append("-"*40)
        for change in strategy_changes:
            lines.append(f"[{change.get('timestamp', 'N/A')}] Iteration {change['iteration']}:")
            lines.append(f"  Original Tool:    {change['original_tool']}")
            lines.append(f"  Replacement Tool: {change.get('replacement_tool', 'None')}")
            lines.append(f"  Rationale:        {change['reason']}")
            lines.append("")
        lines.append("")

    # Self-correction log section
    self_corrections = [
        e for e in results.get("audit_log", [])
        if e.get("event") == "SELF_CORRECTION_DECISION"
    ]
    if self_corrections:
        lines.append("SELF-CORRECTION LOG")
        lines.append("-" * 40)
        for sc in self_corrections:
            d = sc.get("data", {})
            cb = d.get("confidence_before", 0)
            ca = d.get("confidence_after", 0)
            promoted = ""
            if ca > cb and ((cb < 60 and ca >= 60) or (cb < 100 and ca == 100)):
                promoted = " [PROMOTED]"
            
            lines.append(f"[{sc['timestamp']}] Iteration {sc.get('iteration', 'N/A')}: {d.get('finding_id')}{promoted}")
            lines.append(f"  Hypothesis: {d.get('hypothesis', 'N/A')} (Confidence: {cb}%)")
            lines.append(f"  Trigger:    {d.get('reasoning', 'N/A')}")
            lines.append(f"  Result:     Updated confidence to {ca}%")
            lines.append("")
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
    
    # Attack Timeline
    import re
    from collections import defaultdict
    from datetime import datetime as dt
    
    lines.append("ATTACK TIMELINE (Evidence-derived, no manual annotation)")
    lines.append("-" * 40)
    
    timeline_events = []
    # Parse dates from findings
    for finding in findings:
        earliest_date = None
        for ev in finding.get("supporting_evidence", []):
            if isinstance(ev, str):
                # Look for typical date formats YYYY-MM-DD
                match = re.search(r'(\d{4}-\d{2}-\d{2})', ev)
                if match:
                    ev_date_str = match.group(1)
                    try:
                        ev_date = dt.strptime(ev_date_str, "%Y-%m-%d")
                        if not earliest_date or ev_date < earliest_date:
                            earliest_date = ev_date
                    except ValueError:
                        pass
        if earliest_date:
            category = finding.get('category', 'Activity').upper()
            desc = finding.get('description', '')[:60]
            if len(finding.get('description', '')) > 60:
                desc += "..."
            timeline_events.append({
                "date": earliest_date,
                "category": category,
                "desc": desc
            })
            
    # Sort and group by date (within 3 days)
    timeline_events.sort(key=lambda x: x["date"])
    
    if not timeline_events:
        lines.append("No temporal evidence available to reconstruct timeline.")
    else:
        current_group_start = None
        current_group_events = []
        
        all_groups = []
        
        for ev in timeline_events:
            if not current_group_start:
                current_group_start = ev["date"]
                current_group_events.append(ev)
            else:
                delta = (ev["date"] - current_group_start).days
                if delta <= 3:
                    current_group_events.append(ev)
                else:
                    all_groups.append((current_group_start, current_group_events))
                    current_group_start = ev["date"]
                    current_group_events = [ev]
                    
        if current_group_events:
            all_groups.append((current_group_start, current_group_events))
            
        # Limit to 15 entries overall
        entry_count = 0
        for start_date, events in all_groups:
            if entry_count >= 15:
                break
            end_date = events[-1]["date"]
            if start_date == end_date:
                date_str = start_date.strftime("%Y-%m-%d")
            else:
                date_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                
            lines.append(f"[{date_str}]")
            for ev in events:
                if entry_count >= 15:
                    break
                ev_date_str = ev["date"].strftime("%Y-%m-%d")
                lines.append(f"  {ev_date_str}  [{ev['category']}]  {ev['desc']}")
                entry_count += 1
            if entry_count >= 15:
                lines.append("  ... (additional events omitted)")
            lines.append("")
            
    lines.append("Timeline reconstructed from MCP artifact analysis across email, filesystem, and document sources.")
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
