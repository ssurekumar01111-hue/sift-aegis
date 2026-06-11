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

MEMORY_IMAGE = "charlie-2009-11-17.mddramimage"
DISK_IMAGE = "charlie-2009-12-11.E01"
MAX_ITERATIONS = 3
CONFIDENCE_THRESHOLD = 0.75

@dataclass
class Finding:
    id: str
    category: str
    description: str
    confidence: float
    status: str  # CONFIRMED / INFERRED / UNVERIFIED / REJECTED
    supporting_artifacts: list
    contradictions: list
    iteration_found: int
    tool_source: str
    raw_data: dict = field(default_factory=dict)

@dataclass 
class InvestigationState:
    iteration: int = 0
    findings: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    corrections_made: int = 0
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class SIFTAEGISOrchestrator:
    
    def __init__(self):
        self.bridge = MCPBridge()
        self.state = InvestigationState()
        self.audit_log = []
    
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
    
    def score_finding(self, finding: Finding) -> float:
        """Score a finding's confidence based on corroborating evidence."""
        base = finding.confidence
        # Boost for multiple artifacts
        if len(finding.supporting_artifacts) >= 3:
            base = min(base + 0.15, 1.0)
        elif len(finding.supporting_artifacts) >= 2:
            base = min(base + 0.08, 1.0)
        # Penalize for contradictions
        if finding.contradictions:
            base = max(base - 0.20 * len(finding.contradictions), 0.0)
        return round(base, 2)
    
    def classify_finding(self, finding: Finding) -> str:
        """Classify finding status based on confidence and artifacts."""
        if finding.confidence >= 0.85 and len(finding.supporting_artifacts) >= 2:
            return "CONFIRMED"
        elif finding.confidence >= 0.65:
            return "INFERRED"
        elif finding.confidence >= 0.40:
            return "UNVERIFIED"
        else:
            return "REJECTED"
    
    def phase_memory_analysis(self) -> list:
        """Phase 1: Memory forensics."""
        self.log("PHASE_START", {"phase": "memory_analysis"})
        findings = []
        
        # Get process list
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
                    category="Suspicious Process",
                    description=f"Process {proc_name} (PID {pid}) has anomalous parent-child relationship",
                    confidence=0.70,
                    status="UNVERIFIED",
                    supporting_artifacts=[f"pslist:PID:{pid}"],
                    contradictions=[],
                    iteration_found=self.state.iteration,
                    tool_source="get_process_list",
                    raw_data={"pid": pid, "name": proc_name}
                )
                findings.append(finding)
                self.log("FINDING_DETECTED", {
                    "id": finding.id,
                    "description": finding.description,
                    "confidence": finding.confidence
                })
        
        # Get network connections
        net_result = self.run_tool_logged(
            "get_network_connections",
            memory_image=MEMORY_IMAGE
        )
        
        if net_result.get("suspicious_connections"):
            for conn in net_result["suspicious_connections"]:
                finding = Finding(
                    id=f"NET-{conn.get('foreign_addr','unknown')}",
                    category="Suspicious Network Connection",
                    description=f"External connection to {conn.get('foreign_addr')}:{conn.get('foreign_port')} by PID {conn.get('pid')}",
                    confidence=0.65,
                    status="UNVERIFIED",
                    supporting_artifacts=[f"netscan:{conn.get('foreign_addr')}"],
                    contradictions=[],
                    iteration_found=self.state.iteration,
                    tool_source="get_network_connections",
                    raw_data=conn
                )
                findings.append(finding)
        
        # Get registry run keys
        reg_result = self.run_tool_logged(
            "get_registry_run_keys",
            memory_image=MEMORY_IMAGE
        )
        
        if reg_result.get("suspicious_count", 0) > 0:
            for key in reg_result.get("run_keys", []):
                if key.get("suspicious"):
                    finding = Finding(
                        id=f"REG-{key.get('value_name','unknown')}",
                        category="Persistence Mechanism",
                        description=f"Suspicious registry run key: {key.get('value_name')} → {key.get('value_data')}",
                        confidence=0.80,
                        status="UNVERIFIED",
                        supporting_artifacts=[f"registry:{key.get('key_path')}"],
                        contradictions=[],
                        iteration_found=self.state.iteration,
                        tool_source="get_registry_run_keys",
                        raw_data=key
                    )
                    findings.append(finding)
        # Get malfind results — code injection detection
        malfind_result = self.run_tool_logged(
            "get_malfind",
            memory_image=MEMORY_IMAGE
        )
        
        if malfind_result.get("total_count", 0) > 0:
            for entry in malfind_result.get("entries", [])[:10]:
                finding = Finding(
                    id=f"MAL-{entry['pid']}-{entry['address']}",
                    category="Code Injection",
                    description=f"Injected code detected in {entry['process_name']} (PID {entry['pid']}) at {entry['address']} — protection: {entry['protection']}",
                    confidence=0.85,
                    status="UNVERIFIED",
                    supporting_artifacts=[
                        f"malfind:PID:{entry['pid']}",
                        f"malfind:address:{entry['address']}",
                        f"malfind:protection:{entry['protection']}"
                    ],
                    contradictions=[],
                    iteration_found=self.state.iteration,
                    tool_source="get_malfind",
                    raw_data=entry
                )
                findings.append(finding)
                self.log("FINDING_DETECTED", {
                    "id": finding.id,
                    "description": finding.description,
                    "confidence": finding.confidence
                })

        
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
                dll_result = self.run_tool_logged(
                    "get_dll_list",
                    memory_image=MEMORY_IMAGE,
                    pid=pid
                )
                if dll_result.get("suspicious_count", 0) > 0:
                    # Find the matching process finding and boost confidence
                    for finding in findings:
                        if finding.raw_data.get("pid") == pid:
                            finding.supporting_artifacts.append(
                                f"dlllist:PID:{pid}:suspicious_dlls:{dll_result['suspicious_count']}"
                            )
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
                    net_f.supporting_artifacts.append(f"process_correlation:PID:{net_pid}")
                    proc_f.supporting_artifacts.append(f"network_correlation:PID:{net_pid}")
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
                    finding.supporting_artifacts.append(
                        "malfind_correlation:code_injection_confirmed"
                    )
                    finding.confidence = min(finding.confidence + 0.20, 1.0)
                    self.log("CORRELATION_MATCH", {
                        "finding_id": finding.id,
                        "corroborating": "malfind code injection in same PID"
                    })

        
        # Rescore all findings after correlation
        for finding in findings:
            finding.confidence = self.score_finding(finding)
            finding.status = self.classify_finding(finding)
        
        self.log("PHASE_END", {
            "phase": "correlation",
            "confirmed": sum(1 for f in findings if f.status == "CONFIRMED"),
            "inferred": sum(1 for f in findings if f.status == "INFERRED"),
            "unverified": sum(1 for f in findings if f.status == "UNVERIFIED")
        })
        return findings
    
    def phase_self_correction(self, findings: list) -> list:
        """Phase 3: Self-correction loop — re-investigate low confidence findings."""
        self.log("PHASE_START", {"phase": "self_correction"})
        
        low_confidence = [
            f for f in findings 
            if f.status in ["UNVERIFIED"] and f.confidence < CONFIDENCE_THRESHOLD
        ]
        
        self.log("SELF_CORRECTION_TARGETS", {
            "count": len(low_confidence),
            "findings": [f.id for f in low_confidence]
        })
        
        for finding in low_confidence:
            self.log("SELF_CORRECTION_START", {
                "finding_id": finding.id,
                "current_confidence": finding.confidence,
                "reason": "Below confidence threshold, re-investigating"
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
                    if not dll_result.get("error"):
                        finding.supporting_artifacts.append(
                            f"self_correction:dll_verification:PID:{pid}"
                        )
                        # Re-run process list for fresh data
                        proc_result = self.run_tool_logged(
                            "get_process_list",
                            memory_image=MEMORY_IMAGE
                        )
                        if pid in proc_result.get("suspicious_pids", []):
                            finding.supporting_artifacts.append(
                                "self_correction:process_reconfirmed"
                            )
                            finding.confidence = min(finding.confidence + 0.15, 1.0)
                        self.state.corrections_made += 1
            
            elif finding.category == "Suspicious Network Connection":
                # Re-run network scan for verification
                net_result = self.run_tool_logged(
                    "get_network_connections",
                    memory_image=MEMORY_IMAGE
                )
                foreign_addr = finding.raw_data.get("foreign_addr")
                confirmed = any(
                    c.get("foreign_addr") == foreign_addr 
                    for c in net_result.get("suspicious_connections", [])
                )
                if confirmed:
                    finding.supporting_artifacts.append(
                        "self_correction:network_reconfirmed"
                    )
                    finding.confidence = min(finding.confidence + 0.15, 1.0)
                    self.state.corrections_made += 1
                else:
                    finding.status = "REJECTED"
                    finding.contradictions.append("network_scan_not_reproduced")
                    self.log("SELF_CORRECTION_REJECTED", {
                        "finding_id": finding.id,
                        "reason": "Could not reproduce in second scan"
                    })
            
            # Reclassify after correction
            finding.status = self.classify_finding(finding)
            self.log("SELF_CORRECTION_RESULT", {
                "finding_id": finding.id,
                "new_confidence": finding.confidence,
                "new_status": finding.status
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
        
        all_findings = []
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.state.iteration = iteration
            self.log("ITERATION_START", {"iteration": iteration})
            print(f"\n--- Iteration {iteration} ---")
            
            # Phase 1: Memory analysis
            findings = self.phase_memory_analysis()
            all_findings.extend(findings)
            
            # Phase 2: Correlation
            all_findings = self.phase_correlation(all_findings)
            
            # Phase 3: Self-correction
            all_findings = self.phase_self_correction(all_findings)
            
            # Check if all findings are resolved
            unresolved = [
                f for f in all_findings 
                if f.status == "UNVERIFIED"
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
        
        self.log("INVESTIGATION_COMPLETE", {
            "total_tool_calls": len(self.state.tool_calls),
            "total_corrections": self.state.corrections_made,
            "final_findings": len(all_findings)
        })
        
        return {
            "findings": [asdict(f) for f in all_findings],
            "audit_log": self.audit_log,
            "tool_calls": self.state.tool_calls,
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
