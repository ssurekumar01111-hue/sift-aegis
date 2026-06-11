from orchestrator import SIFTAEGISOrchestrator, Finding
from unittest.mock import MagicMock

def test_new_confidence_engine():
    orchestrator = SIFTAEGISOrchestrator()
    
    finding = Finding(
        id="TEST-1",
        title="Test Finding",
        category="Suspicious Process",
        description="Test Description",
        confidence=0.0,
        status="UNVERIFIED",
        evidence_sources=["get_process_list", "get_dll_list", "get_network_connections"]
    )
    
    # Base: process(0.2), dll(0.1), network(0.2) = 0.5
    # Corroboration bonus: Process + DLL + Network = +0.20
    # Hypothesis bonus: Process requires network, dll = +0.10
    # Expected: 0.5 + 0.2 + 0.1 = 0.8
    
    new_conf = orchestrator.calculate_confidence(finding)
    print(f"Confidence: {new_conf}")
    assert new_conf == 0.8

test_new_confidence_engine()
print("Test Passed!")
