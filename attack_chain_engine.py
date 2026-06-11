import json
import os

class AttackChainEngine:
    def __init__(self, graph_path: str):
        self.graph_path = graph_path
        self.graph = self._load_graph()

    def _load_graph(self):
        with open(self.graph_path, 'r') as f:
            return json.load(f)

    def reconstruct(self):
        """Reconstruct attack chain from evidence graph."""
        # Simple implementation: chain findings by confidence and order
        nodes = self.graph.get("nodes", [])
        
        # Sort by confidence (highest first) as a simple heuristic
        chain = sorted(nodes, key=lambda x: x['confidence'], reverse=True)
        
        attack_chain = []
        for node in chain:
            attack_chain.append({
                "step": node["name"],
                "evidence": node["id"],
                "confidence": node["confidence"]
            })
            
        result = {
            "attack_chain": attack_chain,
            "confidence": sum(n['confidence'] for n in chain) / len(chain) if chain else 0
        }
        
        # Save reports
        os.makedirs("reports", exist_ok=True)
        with open("reports/attack_chain.json", "w") as f:
            json.dump(result, f, indent=2)
            
        with open("reports/attack_chain.md", "w") as f:
            f.write("# Attack Chain\n\n")
            for step in result["attack_chain"]:
                f.write(f"- {step['step']} (Evidence: {step['evidence']}, Confidence: {step['confidence']})\n")
        
        return result
