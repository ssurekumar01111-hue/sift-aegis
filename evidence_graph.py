from dataclasses import dataclass, field
from typing import Dict, List, Any
import json

@dataclass
class EvidenceNode:
    id: str
    type: str
    name: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvidenceEdge:
    source: str
    target: str
    relationship: str
    confidence: float
    evidence: str

class EvidenceGraph:
    def __init__(self):
        self.nodes: Dict[str, EvidenceNode] = {}
        self.edges: List[EvidenceEdge] = []

    def add_node(self, node: EvidenceNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: EvidenceEdge):
        self.edges.append(edge)

    def to_dict(self):
        return {
            "nodes": [node.__dict__ for node in self.nodes.values()],
            "edges": [edge.__dict__ for edge in self.edges]
        }

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def validate(self):
        node_count = len(self.nodes)
        edge_count = len(self.edges)
        
        # Calculate orphan nodes: nodes with no incoming or outgoing edges
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
            
        orphan_nodes = [node_id for node_id in self.nodes if node_id not in connected_nodes]
        
        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "orphan_count": len(orphan_nodes)
        }
