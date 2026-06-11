import json
import os

class ReplayEngine:
    def __init__(self, investigation_results_path: str, audit_trail_path: str):
        self.results_path = investigation_results_path
        self.audit_path = audit_trail_path

    def export_replay(self, finding_id: str):
        with open(self.results_path, 'r') as f:
            results = json.load(f)
        
        # Find finding
        finding = next((f for f in results.get("findings", []) if f["finding_id"] == finding_id), None)
        
        if not finding:
            return None
        
        # Extract audit logs for this finding
        audit_logs = []
        with open(self.audit_path, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                # Audit logs have a data dictionary that might have finding_id
                data = log_entry.get("data", {})
                if data.get("finding_id") == finding_id:
                    audit_logs.append(log_entry)
        
        replay_data = {
            "finding_id": finding_id,
            "confidence_history": finding.get("confidence_history", []),
            "reasoning_updates": finding.get("relationship_reasoning", []),
            "final_classification": finding.get("status"),
            "audit_logs": audit_logs
        }
        
        os.makedirs("replay", exist_ok=True)
        with open(f"replay/{finding_id}_replay.json", "w") as f:
            json.dump(replay_data, f, indent=2)
            
        return replay_data
