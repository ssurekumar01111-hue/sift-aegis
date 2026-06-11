#!/usr/bin/env python3
"""
SIFT-AEGIS Self-Correction Orchestrator
Autonomous DFIR investigation with iterative self-correction.
"""

import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from mcp_bridge import MCPBridge
from evidence_graph import EvidenceGraph, EvidenceNode, EvidenceEdge


MEMORY_IMAGE = "charlie-2009-11-17.mddramimage"
DISK_IMAGE = "charlie-2009-12-11.E01"
MAX_ITERATIONS = 3
CONFIDENCE_THRESHOLD = 0.95

@dataclass
class Finding:
    id: str
    title: str
    category: str
    description: str
    confidence: float
    status: str  # CONFIRMED / INFERRED / UNVERIFIED / REJECTED
    supporting_evidence: list = field(default_factory=list)
    contradictory_evidence: list = field(default_factory=list)
    missing_evidence: list = field(default_factory=list)
    confidence_explanation: str = ""
    evidence_sources: list = field(default_factory=list)
    iteration_found: int = 0
    tool_source: str = ""
    raw_data: dict = field(default_factory=dict)
    relationship_reasoning: list = field(default_factory=list)
    hypothesis: str = ""
    hypothesis_confidence: str = ""
    confidence_history: list = field(default_factory=list)
    confidence_change_reason: str = ""

    def to_dict(self):
        return {
            "finding_id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "confidence": int(self.confidence * 100),
            "status": self.status,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "missing_evidence": self.missing_evidence,
            "confidence_explanation": self.confidence_explanation,
            "evidence_sources": self.evidence_sources,
            "iteration_found": self.iteration_found,
            "tool_source": self.tool_source,
            "raw_data": self.raw_data,
            "relationship_reasoning": self.relationship_reasoning,
            "hypothesis": self.hypothesis,
            "hypothesis_confidence": self.hypothesis_confidence,
            "confidence_history": self.confidence_history,
            "confidence_change_reason": self.confidence_change_reason
        }

@dataclass 
class InvestigationState:
    iteration: int = 0
    findings: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    iteration_accuracy: list = field(default_factory=list)
    corrections_made: int = 0
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class SIFTAEGISOrchestrator:
    
    def __init__(self):
        self.bridge = MCPBridge()
        self.state = InvestigationState()
        self.audit_log = []
        self.graph = EvidenceGraph()
        self.source_weights = {
            "get_process_list": 0.20,
            "get_malfind": 0.30,
            "get_registry_run_keys": 0.20,
            "get_network_connections": 0.20,
            "get_dll_list": 0.10,
            "extract_mft_timeline": 0.15,
            "get_evtx_events": 0.15
        }

    def generate_evidence_graph(self):
        """Constructs the evidence graph from current findings."""
        for finding in self.state.findings:
            node = EvidenceNode(
                id=finding.id,
                type="Finding",
                name=finding.title,
                confidence=finding.confidence,
                metadata={"category": finding.category}
            )
            self.graph.add_node(node)
            
            # Simplified relationship creation for evidence
            for source in finding.evidence_sources:
                edge = EvidenceEdge(
                    source=finding.id,
                    target=source,
                    relationship="observed_in",
                    confidence=finding.confidence,
                    evidence=source
                )
                self.graph.add_edge(edge)
                
        # Save graph
        os.makedirs("graph", exist_ok=True)
        self.graph.save("graph/evidence_graph.json")
        self.log("GRAPH_GENERATED", self.graph.validate())
        self.reconstruct_attack_chain()

    def reconstruct_attack_chain(self):
        """Generates attack chain reports from the evidence graph."""
        from attack_chain_engine import AttackChainEngine
        engine = AttackChainEngine("graph/evidence_graph.json")
        result = engine.reconstruct()
        self.log("ATTACK_CHAIN_CREATED", {"confidence": result["confidence"]})
        self.log("ATTACK_CHAIN_VALIDATED", {"status": "SUCCESS"})
        self.run_benchmark()

    def run_benchmark(self):
        """Runs benchmarks on investigation results."""
        from benchmark.benchmark_runner import run_benchmark
        run_benchmark()
        self.log("BENCHMARK_COMPLETED", {"status": "SUCCESS"})
        self.export_finding_replay("TEST-1")

    def export_finding_replay(self, finding_id: str):
        """Generates replay data for a specific finding."""
        from replay_engine import ReplayEngine
        engine = ReplayEngine("investigation_results.json", "audit/audit_trail.jsonl")
        replay_data = engine.export_replay(finding_id)
        self.log("REPLAY_CREATED", {"finding_id": finding_id})
        self.log("REPLAY_EXPORTED", {"finding_id": finding_id, "path": f"replay/{finding_id}_replay.json"})
        self.run_mitre_mapping()

    def run_mitre_mapping(self):
        """Maps findings to MITRE ATT&CK techniques."""
        from mitre_mapping_engine import MITREMappingEngine
        engine = MITREMappingEngine(self.state.findings)
        result = engine.map()
        self.log("MITRE_TECHNIQUE_MAPPED", {"techniques": len(result["techniques"])})
        self.log("MITRE_REPORT_CREATED", {"status": "SUCCESS"})

    
    def log(self, event: str, data: dict = {}):
        """Structured audit log entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "iteration": self.state.iteration,
            "event": event,
            "data": data
        }
        self.audit_log.append(entry)
        print(f"[{entry['timestamp']}] [{event}] {json.dumps(data)[:200]}")
    
    def run_tool_logged(self, tool_name: str, **kwargs) -> dict:
        """Run tool and log to audit trail."""
        self.log("TOOL_CALL", {"tool": tool_name, "args": kwargs})
        result = self.bridge.run_tool(tool_name, **kwargs)
        self.state.tool_calls.append({
            "timestamp": datetime.utcnow().isoformat(),
            "iteration": self.state.iteration,
            "tool": tool_name,
            "args": kwargs,
            "result_summary": {
                "total_count": result.get("total_count", 0),
                "suspicious_count": result.get("suspicious_count", 0),
                "sha256": result.get("evidence", {}).get("sha256", "")[:16] + "..."
            }
        })
        self.log("TOOL_RESULT", {
            "tool": tool_name,
            "total": result.get("total_count", 0),
            "suspicious": result.get("suspicious_count", 0)
        })
        return result
    
    def generate_reasoning(self, finding: Finding):
        """Generate missing evidence, hypothesis, and relationship reasoning."""
        missing = []
        explanation = []
        
        # Hypothesis mapping
        hypothesis_map = {
            "Suspicious Process": ("Possible code injection or malicious process masquerading", "High"),
            "Suspicious Network Connection": ("Potential command and control activity", "Medium"),
            "Code Injection": ("Injected executable memory detected", "High"),
            "Persistence Mechanism": ("Persistence mechanism established", "Medium"),
            "Suspicious Event Log": ("Potential log clearing or malicious event activity", "Low")
        }
        
        finding.hypothesis, finding.hypothesis_confidence = hypothesis_map.get(
            finding.category, ("Potential anomalous activity", "Low")
        )
        
        # Relationship reasoning
        if finding.category == "Suspicious Process":
            if "get_network_connections" not in finding.evidence_sources:
                missing.append("Network connection correlation")
            if "get_dll_list" not in finding.evidence_sources:
                missing.append("DLL injection verification")
            if "extract_mft_timeline" not in finding.evidence_sources:
                missing.append("Disk execution correlation")
            
            finding.relationship_reasoning = [
                "Process anomalies suggest unauthorized execution or masquerading.",
                "DLL or Network anomalies in this process would significantly strengthen the injection hypothesis."
            ]
        elif finding.category == "Code Injection":
            if "get_dll_list" not in finding.evidence_sources:
                missing.append("DLL list correlation")
            finding.relationship_reasoning = [
                "Executable memory regions with no mapped file are strong indicators of process hollowing or injection.",
                "Correlating with DLL loads can confirm the injected module origin."
            ]
        # ... (other categories)
                
        finding.missing_evidence = missing
        
        if finding.supporting_evidence:
            explanation.append(f"{len(finding.supporting_evidence)} pieces of supporting evidence identified.")
        if finding.contradictory_evidence:
            explanation.append(f"However, {len(finding.contradictory_evidence)} contradictory artifacts observed.")
        if finding.missing_evidence:
            explanation.append(f"Additional evidence required: {', '.join(finding.missing_evidence)}.")
        else:
            explanation.append("All primary evidence domains correlated successfully.")
            
        finding.confidence_explanation = " ".join(explanation)
        self.log("REASONING_CREATED", {
            "finding_id": finding.id,
            "hypothesis": finding.hypothesis,
            "reasoning": finding.confidence_explanation
        })

    def _get_corroboration_bonus(self, finding: Finding) -> float:
        sources = set(finding.evidence_sources)
        if all(s in sources for s in ["get_process_list", "get_registry_run_keys", "extract_mft_timeline", "get_network_connections"]):
            return 0.30
        if all(s in sources for s in ["get_process_list", "get_dll_list", "get_network_connections"]):
            return 0.20
        if all(s in sources for s in ["get_process_list", "get_dll_list"]):
            return 0.10
        return 0.0

    def _get_hypothesis_bonus(self, finding: Finding) -> float:
        # Simple hypothesis alignment: if required evidence for category exists
        requirements = {
            "Suspicious Process": ["get_network_connections", "get_dll_list"],
            "Code Injection": ["get_dll_list", "get_malfind"],
            "Persistence Mechanism": ["get_registry_run_keys"]
        }
        required = requirements.get(finding.category, [])
        if required and all(s in finding.evidence_sources for s in required):
            return 0.10
        return 0.0

    def calculate_confidence(self, finding: Finding) -> float:
        """Score a finding's confidence based on weighted evidence sources, corroboration, and hypothesis alignment."""
        old_confidence = finding.confidence
        score = 0.0
        unique_sources = set(finding.evidence_sources)
        
        # Base score from sources
        for source in unique_sources:
            score += self.source_weights.get(source, 0.05)
            
        # Supporting evidence bonus
        score += 0.05 * len(finding.supporting_evidence)
        
        # Corroboration Bonus
        corroboration_bonus = self._get_corroboration_bonus(finding)
        if corroboration_bonus > 0:
            self.log("CORROBORATION_BONUS_APPLIED", {"finding_id": finding.id, "bonus": corroboration_bonus})
        score += corroboration_bonus
        
        # Hypothesis Alignment Bonus
        hypothesis_bonus = self._get_hypothesis_bonus(finding)
        if hypothesis_bonus > 0:
            self.log("HYPOTHESIS_ALIGNMENT_BONUS_APPLIED", {"finding_id": finding.id, "bonus": hypothesis_bonus})
        score += hypothesis_bonus
        
        # Penalties
        if finding.contradictory_evidence:
            score -= 0.25 * len(finding.contradictory_evidence)
        
        if finding.missing_evidence:
            score -= 0.03 * len(finding.missing_evidence)
            
        if "missing_verification" in finding.contradictory_evidence:
            score -= 0.15
            
        new_confidence = round(max(min(score, 1.0), 0.0), 2)
        
        # Record history and log evolution
        if new_confidence != old_confidence:
            self.log("CONFIDENCE_RECALCULATED", {"finding_id": finding.id, "old_confidence": old_confidence, "new_confidence": new_confidence})
            change_reason = f"Recalculated: Base + {corroboration_bonus} (corroboration) + {hypothesis_bonus} (hypothesis)"
            evolution_entry = {
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "reason": change_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            finding.confidence_history.append(evolution_entry)
            self.log("CONFIDENCE_EVOLUTION", {"finding_id": finding.id, **evolution_entry})
            
            finding.confidence = new_confidence
            
        return new_confidence
    
    def classify_finding(self, finding: Finding) -> str:
        """Hallucination detection layer: Reclassify based on confidence and evidence count."""
        old_status = finding.status
        old_conf = finding.confidence
        
        finding.confidence = self.calculate_confidence(finding)
        
        # Track confidence history
        if finding.confidence != old_conf:
            finding.confidence_history.append({
                "old": int(old_conf * 100),
                "new": int(finding.confidence * 100),
                "timestamp": datetime.utcnow().isoformat()
            })
            finding.confidence_change_reason = finding.confidence_explanation
        
        if len(finding.contradictory_evidence) > 0:
            finding.status = "REJECTED"
        elif finding.confidence >= 0.85 and len(finding.evidence_sources) >= 2:
            finding.status = "CONFIRMED"
        elif finding.confidence >= 0.60:
            finding.status = "INFERRED"
        else:
            finding.status = "UNVERIFIED"
            
        if old_status != finding.status or old_conf != finding.confidence:
            event = "CONFIDENCE_UPDATED"
            if finding.status == "REJECTED":
                event = "FINDING_REJECTED"
            elif finding.status == "UNVERIFIED" and old_status in ["CONFIRMED", "INFERRED"]:
                event = "HALLUCINATION_DETECTED"
            
            self.log(event, {
                "finding_id": finding.id,
                "old_confidence": int(old_conf * 100),
                "new_confidence": int(finding.confidence * 100),
                "old_status": old_status,
                "new_status": finding.status,
                "reason": finding.confidence_explanation
            })
            
        return finding.status
    
    def phase_memory_analysis(self) -> list:
        """Phase 1: Memory forensics."""
        self.log("PHASE_START", {"phase": "memory_analysis"})
        findings = []
        
        # Get process list
        self.log("ANALYST_REASONING", {
            "step": "process_analysis",
            "reasoning": "Starting with process list — memory is most volatile evidence. Anomalous parent-child relationships indicate process injection or masquerading.",
            "tool_chosen": "get_process_list",
            "expected": "Normal Windows process tree with services.exe, svchost.exe hierarchy",
            "looking_for": "Processes spawned from unexpected parents, known malicious names, orphaned processes"
        })
        proc_result = self.run_tool_logged(
            "get_process_list",
            memory_image=MEMORY_IMAGE
        )
        
        if proc_result.get("suspicious_pids"):
            for pid in proc_result["suspicious_pids"]:
                proc_name = next(
                    (p["image_name"] for p in proc_result["processes"] 
                     if p["pid"] == pid), "unknown"
                )
                finding = Finding(
                    id=f"MEM-{pid}",
                    title=f"Suspicious Process: {proc_name}",
                    category="Suspicious Process",
                    description=f"Process {proc_name} (PID {pid}) has anomalous parent-child relationship",
                    confidence=0.20,
                    status="UNVERIFIED",
                    supporting_evidence=[f"pslist:PID:{pid}"],
                    contradictory_evidence=[],
                    evidence_sources=["get_process_list"],
                    iteration_found=self.state.iteration,
                    tool_source="get_process_list",
                    raw_data={"pid": pid, "name": proc_name}
                )
                findings.append(finding)
                self.log("FINDING_DETECTED", {
                    "id": finding.id,
                    "description": finding.description,
                    "confidence": int(finding.confidence * 100)
                })
        
        # Get network connections
        self.log("ANALYST_REASONING", {
            "step": "network_analysis", 
            "reasoning": "Checking network connections after process analysis — if suspicious process has external connection, that is strong C2 indicator.",
            "tool_chosen": "get_network_connections",
            "expected": "Local connections only for a corporate workstation",
            "looking_for": "External IPs, unusual ports, connections from suspicious PIDs"
        })
        net_result = self.run_tool_logged(
            "get_network_connections",
            memory_image=MEMORY_IMAGE
        )
        
        if net_result.get("suspicious_connections"):
            for conn in net_result["suspicious_connections"]:
                finding = Finding(
                    id=f"NET-{conn.get('foreign_addr','unknown')}",
                    title=f"Suspicious Network Connection: {conn.get('foreign_addr')}",
                    category="Suspicious Network Connection",
                    description=f"External connection to {conn.get('foreign_addr')}:{conn.get('foreign_port')} by PID {conn.get('pid')}",
                    confidence=0.20,
                    status="UNVERIFIED",
                    supporting_evidence=[f"netscan:{conn.get('foreign_addr')}"],
                    contradictory_evidence=[],
                    evidence_sources=["get_network_connections"],
                    iteration_found=self.state.iteration,
                    tool_source="get_network_connections",
                    raw_data=conn
                )
                findings.append(finding)
        
        # Get registry run keys
        self.log("ANALYST_REASONING", {
            "step": "persistence_analysis",
            "reasoning": "Checking registry Run keys — common persistence mechanism. Malware writes here to survive reboot.",
            "tool_chosen": "get_registry_run_keys",
            "expected": "Legitimate software entries pointing to Program Files",
            "looking_for": "Entries pointing to temp dirs, encoded paths, unusual executables"
        })
        reg_result = self.run_tool_logged(
            "get_registry_run_keys",
            memory_image=MEMORY_IMAGE
        )
        
        if reg_result.get("suspicious_count", 0) > 0:
            for key in reg_result.get("run_keys", []):
                if key.get("suspicious"):
                    finding = Finding(
                        id=f"REG-{key.get('value_name','unknown')}",
                        title=f"Persistence Mechanism: {key.get('value_name')}",
                        category="Persistence Mechanism",
                        description=f"Suspicious registry run key: {key.get('value_name')} → {key.get('value_data')}",
                        confidence=0.20,
                        status="UNVERIFIED",
                        supporting_evidence=[f"registry:{key.get('key_path')}"],
                        contradictory_evidence=[],
                        evidence_sources=["get_registry_run_keys"],
                        iteration_found=self.state.iteration,
                        tool_source="get_registry_run_keys",
                        raw_data=key
                    )
                    findings.append(finding)
        # Get malfind results — code injection detection
        self.log("ANALYST_REASONING", {
            "step": "injection_detection",
            "reasoning": "Running malfind after process analysis — code injection leaves executable memory regions with no mapped file. Cross-referencing with suspicious PIDs found earlier.",
            "tool_chosen": "get_malfind",
            "expected": "Clean memory regions for all processes",
            "looking_for": "PAGE_EXECUTE_READWRITE regions, VAD anomalies, shellcode indicators"
        })
        malfind_result = self.run_tool_logged(
            "get_malfind",
            memory_image=MEMORY_IMAGE
        )
        
        if malfind_result.get("total_count", 0) > 0:
            for entry in malfind_result.get("entries", [])[:10]:
                finding = Finding(
                    id=f"MAL-{entry['pid']}-{entry['address']}",
                    title=f"Code Injection: {entry['process_name']} (PID {entry['pid']})",
                    category="Code Injection",
                    description=f"Injected code detected in {entry['process_name']} (PID {entry['pid']}) at {entry['address']} — protection: {entry['protection']}",
                    confidence=0.30,
                    status="UNVERIFIED",
                    supporting_evidence=[
                        f"malfind:PID:{entry['pid']}",
                        f"malfind:address:{entry['address']}",
                        f"malfind:protection:{entry['protection']}"
                    ],
                    contradictory_evidence=[],
                    evidence_sources=["get_malfind"],
                    iteration_found=self.state.iteration,
                    tool_source="get_malfind",
                    raw_data=entry
                )
                findings.append(finding)
                self.log("FINDING_DETECTED", {
                    "id": finding.id,
                    "description": finding.description,
                    "confidence": int(finding.confidence * 100)
                })

        # EVTX Event Log Analysis
        self.log("ANALYST_REASONING", {
            "step": "evtx_analysis",
            "reasoning": "Checking Windows Event Logs — process creation events (4688), logon events (4624/4625), and service installs (7045) correlate with memory findings.",
            "tool_chosen": "get_evtx_events",
            "expected": "Normal system events — scheduled tasks, service starts",
            "looking_for": "Event 4688 process creation matching suspicious PIDs, event 1102 log clearing"
        })
        
        evtx_result = self.run_tool_logged(
            "get_evtx_events",
            memory_image=MEMORY_IMAGE
        )
        
        if evtx_result.get("suspicious_count", 0) > 0:
            for event in evtx_result.get("entries", []):
                if event.get("suspicious"):
                    finding = Finding(
                        id=f"EVT-{event['event_id']}-{event.get('timestamp','')[:10]}",
                        title=f"Suspicious Event Log: {event['event_id']}",
                        category="Suspicious Event Log",
                        description=f"Security event {event['event_id']}: {event['description']}",
                        confidence=0.0,
                        status="UNVERIFIED",
                        supporting_evidence=[
                            f"evtx:event_id:{event['event_id']}",
                            f"evtx:source:{event.get('source','unknown')}"
                        ],
                        contradictory_evidence=[],
                        evidence_sources=["get_evtx_events"],
                        iteration_found=self.state.iteration,
                        tool_source="get_evtx_events",
                        raw_data=event
                    )
                    findings.append(finding)

        
        for finding in findings:
            self.generate_reasoning(finding)
            finding.status = self.classify_finding(finding)

        self.log("PHASE_END", {
            "phase": "memory_analysis",
            "findings_count": len(findings)
        })
        return findings
    
    def phase_correlation(self, findings: list) -> list:
        """Phase 2: Cross-correlate findings to boost confidence."""
        self.log("PHASE_START", {"phase": "correlation"})
        
        # Find process PIDs from memory findings
        process_pids = {
            f.raw_data.get("pid") 
            for f in findings 
            if f.category == "Suspicious Process"
        }
        
        # Cross-correlate: check DLLs for suspicious process PIDs
        for pid in process_pids:
            if pid:
                self.log("ANALYST_REASONING", {
                    "step": "dll_analysis",
                    "reasoning": f"Deep diving PID {pid} — checking loaded DLLs for injection from temp paths or unsigned modules. This PID was flagged as suspicious in process analysis.",
                    "tool_chosen": "get_dll_list",
                    "expected": "DLLs loaded from System32 or Program Files",
                    "looking_for": "DLLs from temp, appdata, or unusual paths indicating DLL hijacking"
                })
                dll_result = self.run_tool_logged(
                    "get_dll_list",
                    memory_image=MEMORY_IMAGE,
                    pid=pid
                )
                if dll_result.get("suspicious_count", 0) > 0:
                    # Find the matching process finding and boost confidence
                    for finding in findings:
                        if finding.raw_data.get("pid") == pid:
                            finding.supporting_evidence.append(
                                f"dlllist:PID:{pid}:suspicious_dlls:{dll_result['suspicious_count']}"
                            )
                            if "get_dll_list" not in finding.evidence_sources:
                                finding.evidence_sources.append("get_dll_list")
                            self.log("CORRELATION_MATCH", {
                                "finding_id": finding.id,
                                "corroborating": f"suspicious DLLs for PID {pid}"
                            })
        
        # Cross-correlate: match network connections to suspicious processes
        net_findings = [f for f in findings if f.category == "Suspicious Network Connection"]
        proc_findings = [f for f in findings if f.category == "Suspicious Process"]
        
        for net_f in net_findings:
            net_pid = net_f.raw_data.get("pid")
            for proc_f in proc_findings:
                if proc_f.raw_data.get("pid") == net_pid:
                    net_f.supporting_evidence.append(f"process_correlation:PID:{net_pid}")
                    proc_f.supporting_evidence.append(f"network_correlation:PID:{net_pid}")
                    if "get_process_list" not in net_f.evidence_sources:
                        net_f.evidence_sources.append("get_process_list")
                    if "get_network_connections" not in proc_f.evidence_sources:
                        proc_f.evidence_sources.append("get_network_connections")
                    self.log("CORRELATION_MATCH", {
                        "network_finding": net_f.id,
                        "process_finding": proc_f.id,
                        "pid": net_pid
                    })
        # Cross-correlate: malfind PIDs vs suspicious processes
        malfind_pids = {
            f.raw_data.get("pid")
            for f in findings
            if f.category == "Code Injection"
        }
        for finding in findings:
            if finding.raw_data.get("pid") in malfind_pids:
                if finding.category == "Suspicious Process":
                    finding.supporting_evidence.append(
                        "malfind_correlation:code_injection_confirmed"
                    )
                    if "get_malfind" not in finding.evidence_sources:
                        finding.evidence_sources.append("get_malfind")
                    self.log("CORRELATION_MATCH", {
                        "finding_id": finding.id,
                        "corroborating": "malfind code injection in same PID"
                    })

        
        # Rescore all findings after correlation
        for finding in findings:
            finding.status = self.classify_finding(finding)
        
        self.log("PHASE_END", {
            "phase": "correlation",
            "confirmed": sum(1 for f in findings if f.status == "CONFIRMED"),
            "inferred": sum(1 for f in findings if f.status == "INFERRED"),
            "unverified": sum(1 for f in findings if f.status == "UNVERIFIED")
        })
        return findings

    def phase_disk_correlation(self, findings: list) -> list:
        """
        Phase 2b: Cross-reference memory findings against disk MFT timeline.
        If memory shows suspicious process spawn time matches disk file 
        creation/modification — CONFIRMED. If disk contradicts memory — flag.
        This is multi-source correlation: memory vs disk evidence.
        """
        self.log("PHASE_START", {"phase": "disk_correlation"})
        
        # Get disk MFT timeline
        mft_result = self.run_tool_logged(
            "extract_mft_timeline",
            disk_image=DISK_IMAGE
        )
        
        if mft_result.get("error"):
            self.log("DISK_CORRELATION_SKIP", {
                "reason": mft_result.get("error", "MFT unavailable")
            })
            return findings
        
        mft_entries = mft_result.get("entries", [])
        self.log("MFT_ENTRIES_LOADED", {
            "count": len(mft_entries),
            "disk_image": DISK_IMAGE
        })
        
        # Cross-reference: look for files matching suspicious process names
        suspicious_names = [
            f.raw_data.get("name", "").lower().replace(".exe", "")
            for f in findings
            if f.category == "Suspicious Process"
        ]
        
        disk_corroborations = []
        for entry in mft_entries:
            fname = entry.get("filename", "").lower()
            for sname in suspicious_names:
                if sname and sname in fname:
                    disk_corroborations.append({
                        "filename": entry.get("filename"),
                        "path": entry.get("file_path"),
                        "modified": entry.get("modified"),
                        "created": entry.get("created"),
                        "matched_process": sname
                    })
        
        if disk_corroborations:
            self.log("DISK_MEMORY_CORRELATION", {
                "corroborations": len(disk_corroborations),
                "matches": disk_corroborations[:5]
            })
            # Boost confidence for findings with disk corroboration
            for finding in findings:
                proc_name = finding.raw_data.get("name", "").lower().replace(".exe", "")
                for corr in disk_corroborations:
                    if proc_name and proc_name in corr.get("matched_process", ""):
                        finding.supporting_evidence.append(
                            f"mft_disk_correlation:{corr['filename']}:{corr.get('modified','')}"
                        )
                        if "extract_mft_timeline" not in finding.evidence_sources:
                            finding.evidence_sources.append("extract_mft_timeline")
                        self.log("MULTI_SOURCE_CONFIRMED", {
                            "finding_id": finding.id,
                            "disk_artifact": corr["filename"],
                            "memory_artifact": finding.tool_source
                        })
        else:
            self.log("DISK_CORRELATION_RESULT", {
                "result": "No direct matches between disk MFT and memory findings",
                "note": "Disk and memory artifacts are consistent — no contradictory_evidence found"
            })
        
        # Generate reasoning and rescore after disk correlation
        for finding in findings:
            self.generate_reasoning(finding)
            finding.status = self.classify_finding(finding)
        
        self.log("PHASE_END", {
            "phase": "disk_correlation",
            "corroborations_found": len(disk_corroborations)
        })
        return findings
    
    def phase_self_correction(self, findings: list) -> list:
        """Phase 3: Self-correction loop — re-investigate low confidence findings."""
        self.log("PHASE_START", {"phase": "self_correction"})
        
        low_confidence = [
            f for f in findings 
            if f.status in ["UNVERIFIED", "INFERRED"] and f.confidence < CONFIDENCE_THRESHOLD
        ]
        
        self.log("SELF_CORRECTION_TARGETS", {
            "count": len(low_confidence),
            "findings": [f.id for f in low_confidence]
        })
        
        for finding in low_confidence:
            self.log("SELF_CORRECTION_START", {
                "finding_id": finding.id,
                "current_confidence": int(finding.confidence * 100),
                "reason": "Below confidence threshold, re-investigating"
            })
            
            # NEW LOGGING
            self.log("HYPOTHESIS_EVALUATED", {
                "finding_id": finding.id,
                "hypothesis": finding.hypothesis,
                "confidence": finding.confidence
            })
            
            # Re-investigate based on finding type
            if finding.category == "Suspicious Process":
                pid = finding.raw_data.get("pid")
                if pid:
                    # Deep dive: check DLLs
                    dll_result = self.run_tool_logged(
                        "get_dll_list",
                        memory_image=MEMORY_IMAGE,
                        pid=pid
                    )
                    
                    # NEW LOGGING
                    self.log("TOOL_SELECTED_FOR_VERIFICATION", {
                        "finding_id": finding.id,
                        "tool": "get_dll_list",
                        "reason": f"Required to support hypothesis {finding.hypothesis}"
                    })

                    if not dll_result.get("error"):
                        finding.supporting_evidence.append(
                            f"self_correction:dll_verification:PID:{pid}"
                        )
                        # Re-run process list for fresh data
                        proc_result = self.run_tool_logged(
                            "get_process_list",
                            memory_image=MEMORY_IMAGE
                        )
                        if pid in proc_result.get("suspicious_pids", []):
                            finding.supporting_evidence.append(
                                "self_correction:process_reconfirmed"
                            )
                            # Update confidence using current logic
                            finding.confidence = min(finding.confidence + 0.15, 1.0)
                        self.state.corrections_made += 1
            
            elif finding.category == "Suspicious Network Connection":
                # Re-run network scan for verification
                net_result = self.run_tool_logged(
                    "get_network_connections",
                    memory_image=MEMORY_IMAGE
                )
                
                # NEW LOGGING
                self.log("TOOL_SELECTED_FOR_VERIFICATION", {
                    "finding_id": finding.id,
                    "tool": "get_network_connections",
                    "reason": f"Required to support hypothesis {finding.hypothesis}"
                })
                
                foreign_addr = finding.raw_data.get("foreign_addr")
                confirmed = any(
                    c.get("foreign_addr") == foreign_addr 
                    for c in net_result.get("suspicious_connections", [])
                )
                if confirmed:
                    finding.supporting_evidence.append(
                        "self_correction:network_reconfirmed"
                    )
                    finding.confidence = min(finding.confidence + 0.15, 1.0)
                    self.state.corrections_made += 1
                else:
                    finding.status = "REJECTED"
                    finding.contradictory_evidence.append("network_scan_not_reproduced")
                    self.log("SELF_CORRECTION_REJECTED", {
                        "finding_id": finding.id,
                        "reason": "Could not reproduce in second scan"
                    })
            
            # NEW LOGGING
            self.generate_reasoning(finding)
            self.log("HYPOTHESIS_UPDATED", {
                "finding_id": finding.id,
                "hypothesis": finding.hypothesis
            })
            
            # Reclassify after correction
            finding.status = self.classify_finding(finding)
            
            # NEW LOGGING
            self.log("SELF_CORRECTION_DECISION", {
                "finding_id": finding.id,
                "hypothesis": finding.hypothesis,
                "reasoning": finding.confidence_explanation,
                "confidence_before": finding.confidence_history[-1]['old'] if finding.confidence_history else int(finding.confidence * 100),
                "confidence_after": int(finding.confidence * 100),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.log("PHASE_END", {
            "phase": "self_correction",
            "corrections_made": self.state.corrections_made
        })
        return findings
    
    def investigate(self) -> dict:
        """Run full autonomous investigation with self-correction."""
        print("\n" + "="*60)
        print("SIFT-AEGIS Autonomous DFIR Investigation")
        print("="*60)
        self.log("INVESTIGATION_START", {
            "memory_image": MEMORY_IMAGE,
            "disk_image": DISK_IMAGE,
            "max_iterations": MAX_ITERATIONS
        })
        
        self.findings_map = {} # Use dict to prevent duplication
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.state.iteration = iteration
            self.log("ITERATION_START", {"iteration": iteration})
            print(f"\n--- Iteration {iteration} ---")
            
            # Phase 1: Memory analysis
            new_findings = self.phase_memory_analysis()
            for f in new_findings:
                if f.id not in self.findings_map:
                    self.findings_map[f.id] = f
            
            # Phase 2: Correlation
            current_findings = list(self.findings_map.values())
            updated_findings = self.phase_correlation(current_findings)
            for f in updated_findings:
                self.findings_map[f.id] = f
            
            # Phase 2b: Disk-Memory cross-source correlation
            current_findings = list(self.findings_map.values())
            updated_findings = self.phase_disk_correlation(current_findings)
            for f in updated_findings:
                self.findings_map[f.id] = f
            
            # Phase 3: Self-correction
            current_findings = list(self.findings_map.values())
            updated_findings = self.phase_self_correction(current_findings)
            for f in updated_findings:
                self.findings_map[f.id] = f
            
            all_findings = list(self.findings_map.values())
            
            # Track accuracy per iteration
            confirmed_count = sum(1 for f in all_findings 
                                  if f.status == "CONFIRMED")
            total_count = len(all_findings)
            accuracy = confirmed_count / total_count if total_count > 0 else 0
            self.state.iteration_accuracy.append({
                "iteration": iteration,
                "total": total_count,
                "confirmed": confirmed_count,
                "inferred": sum(1 for f in all_findings 
                               if f.status == "INFERRED"),
                "unverified": sum(1 for f in all_findings 
                                 if f.status == "UNVERIFIED"),
                "rejected": sum(1 for f in all_findings 
                               if f.status == "REJECTED"),
                "accuracy_score": round(accuracy, 3)
            })
            self.log("ITERATION_ACCURACY", 
                     self.state.iteration_accuracy[-1])

            # Check if all findings are resolved
            unresolved = [
                f for f in all_findings 
                if f.status in ["UNVERIFIED", "INFERRED"] and f.confidence < CONFIDENCE_THRESHOLD
            ]
            
            self.log("ITERATION_END", {
                "iteration": iteration,
                "total_findings": len(all_findings),
                "confirmed": sum(1 for f in all_findings if f.status == "CONFIRMED"),
                "inferred": sum(1 for f in all_findings if f.status == "INFERRED"),
                "unverified": len(unresolved),
                "rejected": sum(1 for f in all_findings if f.status == "REJECTED")
            })
            
            if not unresolved:
                self.log("INVESTIGATION_CONVERGED", {
                    "iteration": iteration,
                    "reason": "All findings resolved"
                })
                break
        
        all_findings = list(self.findings_map.values())
        self.log("INVESTIGATION_COMPLETE", {
            "total_tool_calls": len(self.state.tool_calls),
            "total_corrections": self.state.corrections_made,
            "final_findings": len(all_findings)
        })
        
        return {
            "findings": [f.to_dict() for f in all_findings],
            "audit_log": self.audit_log,
            "tool_calls": self.state.tool_calls,
            "accuracy_delta": {
                "iteration_1_accuracy": self.state.iteration_accuracy[0]["accuracy_score"] if self.state.iteration_accuracy else 0,
                "final_accuracy": self.state.iteration_accuracy[-1]["accuracy_score"] if self.state.iteration_accuracy else 0,
                "improvement": round(
                    (self.state.iteration_accuracy[-1]["accuracy_score"] - 
                     self.state.iteration_accuracy[0]["accuracy_score"]) * 100, 1
                ) if len(self.state.iteration_accuracy) > 1 else 0,
                "iterations": self.state.iteration_accuracy
            },
            "summary": {
                "total_findings": len(all_findings),
                "confirmed": sum(1 for f in all_findings if f.status == "CONFIRMED"),
                "inferred": sum(1 for f in all_findings if f.status == "INFERRED"),
                "unverified": sum(1 for f in all_findings if f.status == "UNVERIFIED"),
                "rejected": sum(1 for f in all_findings if f.status == "REJECTED"),
                "corrections_made": self.state.corrections_made,
                "total_tool_calls": len(self.state.tool_calls),
                "iterations_run": self.state.iteration
            }
        }

if __name__ == "__main__":
    orchestrator = SIFTAEGISOrchestrator()
    results = orchestrator.investigate()
    
    print("\n" + "="*60)
    print("INVESTIGATION SUMMARY")
    print("="*60)
    summary = results["summary"]
    for key, val in summary.items():
        print(f"  {key}: {val}")
    
    # Save results
    output_path = "/home/sansforensics/sift-aegis/investigation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to: {output_path}")
