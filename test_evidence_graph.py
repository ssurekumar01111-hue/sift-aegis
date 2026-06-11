from orchestrator import SIFTAEGISOrchestrator, Finding
from unittest.mock import MagicMock
import os
import json

def test_graph_generation():
    orchestrator = SIFTAEGISOrchestrator()
    
    # Mock some findings
    finding1 = Finding(
        id="TEST-1",
        title="Test Finding 1",
        category="Suspicious Process",
        description="Test Description",
        confidence=0.8,
        status="CONFIRMED",
        evidence_sources=["get_process_list", "get_dll_list"]
    )
    
    orchestrator.state.findings = [finding1]
    
    # Generate graph
    orchestrator.generate_evidence_graph()
    
    # Validate file
    assert os.path.exists("graph/evidence_graph.json")
    print("Graph file generated.")
    
    # Read and print graph nodes/edges
    with open("graph/evidence_graph.json", "r") as f:
        graph_data = json.load(f)
        print("Nodes:", graph_data["nodes"])
        print("Edges:", graph_data["edges"])

test_graph_generation()
