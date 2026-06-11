import sys
import os
import json

# Add root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import Finding
from mitre_mapping_engine import MITREMappingEngine

def run_mitre():
    with open('/home/sansforensics/sift-aegis/investigation_results.json', 'r') as f:
        data = json.load(f)
    
    findings = []
    for f_dict in data.get("findings", []):
        # Convert dictionary to Finding object
        finding = Finding(
            id=f_dict["finding_id"],
            title=f_dict["title"],
            category=f_dict["category"],
            description=f_dict["description"],
            confidence=f_dict["confidence"] / 100.0,
            status=f_dict["status"],
            supporting_evidence=f_dict["supporting_evidence"],
            contradictory_evidence=f_dict["contradictory_evidence"],
            missing_evidence=f_dict["missing_evidence"],
            confidence_explanation=f_dict["confidence_explanation"],
            evidence_sources=f_dict["evidence_sources"],
            iteration_found=f_dict["iteration_found"],
            tool_source=f_dict["tool_source"],
            raw_data=f_dict["raw_data"],
            relationship_reasoning=f_dict["relationship_reasoning"],
            hypothesis=f_dict["hypothesis"],
            hypothesis_confidence=f_dict["hypothesis_confidence"],
            confidence_history=f_dict["confidence_history"],
            confidence_change_reason=f_dict["confidence_change_reason"]
        )
        findings.append(finding)
    
    engine = MITREMappingEngine(findings)
    result = engine.map()
    
    print("MITRE mapping generated.")
    print(f"Techniques identified: {len(result['techniques'])}")

if __name__ == "__main__":
    run_mitre()
