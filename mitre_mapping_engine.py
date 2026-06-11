import json
import os

class MITREMappingEngine:
    def __init__(self, findings):
        self.findings = findings
        self.mapping = {
            "Suspicious Process": "T1059.003",
            "Code Injection": "T1055",
            "Persistence Mechanism": "T1547.001"
        }

    def map(self):
        techniques = []
        confidence_map = {}
        for f in self.findings:
            category = f.category
            if category in self.mapping:
                technique = self.mapping[category]
                techniques.append({"finding_id": f.id, "technique": technique})
                confidence_map[technique] = f.confidence
        
        result = {"techniques": techniques, "confidence": confidence_map}
        
        os.makedirs("reports", exist_ok=True)
        with open("reports/mitre_mapping.json", "w") as f:
            json.dump(result, f, indent=2)
        with open("reports/mitre_mapping.md", "w") as f:
            f.write("# MITRE ATT&CK Mapping\n\n")
            for t in techniques:
                f.write(f"- Finding {t['finding_id']} -> {t['technique']}\n")
        
        return result
