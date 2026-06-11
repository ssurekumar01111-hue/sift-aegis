import re

with open("reports/report_generator.py", "r") as f:
    code = f.read()

def create_finding_block(status):
    return f"""        for i, f in enumerate({status.lower()}, 1):
            lines.append(f"[{{i}}] [{status}] {{f['title']}}")
            lines.append(f"    Finding ID:  {{f['finding_id']}}")
            lines.append(f"    Confidence:  {{f['confidence']}}%")
            lines.append(f"    Category:    {{f.get('category', 'N/A')}}")
            lines.append(f"    Description: {{f.get('description', 'N/A')}}")
            lines.append(f"    Supporting Evidence:")
            if f.get('supporting_evidence'):
                for ev in f.get('supporting_evidence', []):
                    lines.append(f"      - {{ev}}")
            else:
                lines.append("      - None")
            lines.append(f"    Contradictory Evidence:")
            if f.get('contradictory_evidence'):
                for ev in f.get('contradictory_evidence', []):
                    lines.append(f"      - {{ev}}")
            else:
                lines.append("      - None")
            lines.append(f"    Missing Evidence:")
            if f.get('missing_evidence'):
                for ev in f.get('missing_evidence', []):
                    lines.append(f"      - {{ev}}")
            else:
                lines.append("      - None")
            lines.append(f"    Confidence Explanation:")
            lines.append(f"      {{f.get('confidence_explanation', 'No explanation provided.')}}")
            lines.append("")"""

old_confirmed = """        for i, f in enumerate(confirmed, 1):
            lines.append(f"[{i}] [CONFIRMED] {f['title']}")
            lines.append(f"    Finding ID:  {f['finding_id']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Category:    {f['category']}")
            lines.append(f"    Description: {f['description']}")
            lines.append(f"    Evidence:    {f['supporting_artifacts']} artifacts from {', '.join(f['evidence_sources'])}")
            lines.append(f"    Reasoning:   {f['reasoning']}")
            lines.append(f"    Detected:    Iteration {f['iteration_found']}")
            lines.append("")"""

old_inferred = """        for i, f in enumerate(inferred, 1):
            lines.append(f"[{i}] [INFERRED] {f['title']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Reasoning:   {f['reasoning']}")
            lines.append(f"    Description: {f['description']}")
            lines.append("")"""

old_unverified = """        for i, f in enumerate(unverified, 1):
            lines.append(f"[{i}] [UNVERIFIED] {f['title']}")
            lines.append(f"    Confidence:  {f['confidence']}%")
            lines.append(f"    Reasoning:   {f['reasoning']}")
            lines.append("")"""

old_rejected = """        for i, f in enumerate(rejected, 1):
            lines.append(f"[{i}] [REJECTED] {f['title']}")
            lines.append(f"    Reasoning:   {f['reasoning']}")
            lines.append(f"    Description: {f['description']}")
            lines.append("")"""

code = code.replace(old_confirmed, create_finding_block("CONFIRMED"))
code = code.replace(old_inferred, create_finding_block("INFERRED"))
code = code.replace(old_unverified, create_finding_block("UNVERIFIED"))
code = code.replace(old_rejected, create_finding_block("REJECTED"))

with open("reports/report_generator.py", "w") as f:
    f.write(code)

