from orchestrator import SIFTAEGISOrchestrator, Finding
from unittest.mock import MagicMock

def simulate_corroboration():
    orchestrator = SIFTAEGISOrchestrator()
    
    # Representative of a finding needing corroboration
    finding = Finding(
        id="MEM-3908",
        title="Suspicious Process: cmd.exe",
        category="Suspicious Process",
        description="Process cmd.exe (PID 3908) has anomalous parent-child relationship",
        confidence=0.25, # From JSON
        status="UNVERIFIED",
        evidence_sources=["get_process_list"] # Originally only has this
    )
    
    print(f"Confidence Before: {finding.confidence}")
    
    # Force adding corroborating sources
    finding.evidence_sources.extend(["get_dll_list", "get_network_connections"])
    
    new_conf = orchestrator.calculate_confidence(finding)
    
    print(f"Evidence Sources: {finding.evidence_sources}")
    print(f"Corroboration Bonus: {orchestrator._get_corroboration_bonus(finding)}")
    print(f"Hypothesis Bonus: {orchestrator._get_hypothesis_bonus(finding)}")
    print(f"Confidence After: {new_conf}")

simulate_corroboration()
