import json
import sys
import os

# Add root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evidence_graph import EvidenceGraph, EvidenceNode, EvidenceEdge

def generate_real_graph():
    with open('/home/sansforensics/sift-aegis/investigation_results.json', 'r') as f:
        data = json.load(f)
    
    graph = EvidenceGraph()
    
    findings = data.get("findings", [])
    
    for finding in findings:
        # Create node for finding
        node = EvidenceNode(
            id=finding['finding_id'],
            type="Finding",
            name=finding['title'],
            confidence=finding['confidence'] / 100.0,
            metadata={"category": finding['category'], "description": finding['description']}
        )
        graph.add_node(node)
        
        # Create edges for supporting evidence
        for evidence in finding.get('supporting_evidence', []):
            edge = EvidenceEdge(
                source=evidence,
                target=finding['finding_id'],
                relationship="supports",
                confidence=finding['confidence'] / 100.0,
                evidence=evidence
            )
            graph.add_edge(edge)
            
            # Create a node for the evidence source if it doesn't exist
            if evidence not in graph.nodes:
                source_node = EvidenceNode(
                    id=evidence,
                    type="EvidenceSource",
                    name=evidence,
                    confidence=1.0
                )
                graph.add_node(source_node)
                
    # Save the graph
    os.makedirs("graph", exist_ok=True)
    graph.save("graph/evidence_graph.json")
    print("Graph generated and saved to graph/evidence_graph.json")

if __name__ == "__main__":
    generate_real_graph()
