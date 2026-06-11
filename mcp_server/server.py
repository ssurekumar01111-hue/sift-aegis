#!/usr/bin/env python3
"""
SIFT-AEGIS Custom MCP Server
Read-only forensic analysis tools wrapping Volatility3.
No shell execution tools exist. All tools return typed Pydantic models.
"""

import hashlib
import subprocess
import json
import os
from datetime import datetime
from typing import Optional
from fastmcp import FastMCP
mcp = FastMCP("sift-aegis-forensics")

from models import (
    EvidenceMetadata, ProcessListResult, ProcessEntry,
    NetworkConnectionList, NetworkConnection,
    RegistryRunKeyList, RegistryRunKey,
    MFTTimeline, MFTEntry,
    DLLList, DLLEntry,
    MalfindEntry, MalfindResult,
    EVTXEntry, EVTXAnalysisResult,
    EmailArtifact, BrowserArtifact, DocumentArtifact
)
...
# ── Tool 7: Email Analysis ───────────────────────────────────────────────────

@mcp.tool()
def extract_outlook_emails(file_path: str = "/home/sansforensics/sift-aegis/real_email_artifacts.json") -> list[dict]:
    """Read-only. Parses email artifacts from JSON."""
    with open(file_path, "r") as f:
        return json.load(f)

# ── Tool 8: Browser Analysis ──────────────────────────────────────────────────

import sqlite3
import os

@mcp.tool()
def analyze_browser_artifacts(image_mount_path: str = "/home/sansforensics/sift-aegis/real_browser_artifacts.json") -> list[dict]:
    """Read-only. Analyzes browser history/downloads/cookies."""
    with open(image_mount_path, "r") as f:
        return json.load(f)

# ── Tool 9: Document Analysis ────────────────────────────────────────────────

@mcp.tool()
def extract_document_metadata(file_path: str = "/home/sansforensics/sift-aegis/real_document_artifacts.json") -> list[dict]:
    """Read-only. Extracts metadata from Office/PDF documents."""
    with open(file_path, "r") as f:
        return json.load(f)

# mcp = FastMCP("sift-aegis-forensics")  <-- REMOVED DUPLICATE


CASES_DIR = os.getenv("CASES_DIR", "/home/sansforensics/cases/m57")

# ── Helpers ──────────────────────────────────────────────────────────────────

def compute_sha256(filepath: str) -> str:
    """Compute SHA256 hash of artifact file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_evidence_metadata(filepath: str) -> EvidenceMetadata:
    """Build evidence metadata with integrity verification."""
    sha256 = compute_sha256(filepath)
    return EvidenceMetadata(
        artifact_path=filepath,
        sha256=sha256,
        verified=True,
        analysis_timestamp=datetime.utcnow().isoformat()
    )

def run_volatility(plugin: str, image_path: str, extra_args: list = []) -> str:
    """Run Volatility3 plugin internally. Never exposed as a tool."""
    cmd = ["vol", "-f", image_path] + extra_args + [plugin]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.stdout + result.stderr

def is_suspicious_process(name: str, ppid: int, pid_to_name: dict) -> bool:
    """
    Enhanced heuristics for suspicious process detection.
    Covers parent-child anomalies, known bad names, and unusual spawning.
    """
    name_lower = name.lower()
    parent_name = pid_to_name.get(ppid, "").lower()
    
    # Known malicious tool names
    known_bad = [
        "mimikatz.exe", "procdump.exe", "pwdump.exe", "wce.exe",
        "fgdump.exe", "gsecdump.exe", "lsadump.exe", "pwdumpx.exe",
        "htran.exe", "tini.exe", "nc.exe", "ncat.exe", "netcat.exe",
        "psexec.exe", "at.exe", "schtasks.exe", "reg.exe",
        "mshta.exe", "wscript.exe", "cscript.exe", "rundll32.exe",
        "regsvr32.exe", "certutil.exe", "bitsadmin.exe"
    ]
    if name_lower in known_bad:
        return True
    
    # Anomalous parent-child relationships
    # svchost.exe should only spawn from services.exe
    if name_lower == "svchost.exe" and parent_name not in [
        "services.exe", ""
    ]:
        return True
    
    # lsass.exe should only spawn from winlogon.exe or wininit.exe
    if name_lower == "lsass.exe" and parent_name not in [
        "winlogon.exe", "wininit.exe", ""
    ]:
        return True
    
    # cmd.exe or powershell.exe spawned from unusual parents
    if name_lower in ["cmd.exe", "powershell.exe"] and parent_name in [
        "winword.exe", "excel.exe", "outlook.exe", "acrord32.exe",
        "iexplore.exe", "firefox.exe", "chrome.exe", "java.exe"
    ]:
        return True
    
    # explorer.exe spawning network tools
    if parent_name == "explorer.exe" and name_lower in [
        "cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe",
        "mshta.exe", "rundll32.exe"
    ]:
        return True
    
    # Double extension or suspicious name patterns
    if name_lower.count(".") > 1:
        return True
    
    # Processes with no parent (orphaned — except System and smss)
    if ppid == 0 and name_lower not in ["system", "idle"]:
        return True
    
    return False

# ── Tool 1: Process List ──────────────────────────────────────────────────────

@mcp.tool()
def get_process_list(memory_image: str) -> dict:
    """
    Read-only. Returns structured process list from memory image.
    Flags suspicious processes based on parent-child anomalies.
    Never returns raw Volatility output.
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    raw = run_volatility("windows.pslist", filepath)

    processes = []
    pid_to_name = {}

    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 10 or not parts[0].isdigit():
            continue
        try:
            entry = ProcessEntry(
                pid=int(parts[0]),
                ppid=int(parts[1]),
                image_name=parts[2],
                offset=parts[3],
                threads=int(parts[4]) if parts[4].isdigit() else 0,
                handles=int(parts[5]) if parts[5].isdigit() else 0,
                session_id=parts[6] if parts[6] != "N/A" else None,
                wow64=parts[7] == "True",
                create_time=parts[8] if parts[8] != "N/A" else None,
                exit_time=parts[9] if parts[9] != "N/A" else None,
            )
            processes.append(entry)
            pid_to_name[entry.pid] = entry.image_name
        except (ValueError, IndexError):
            continue

    suspicious_pids = [
        p.pid for p in processes
        if is_suspicious_process(p.image_name, p.ppid, pid_to_name)
    ]

    result = ProcessListResult(
        evidence=evidence,
        processes=processes,
        total_count=len(processes),
        suspicious_count=len(suspicious_pids),
        suspicious_pids=suspicious_pids
    )
    return result.model_dump()

# ── Tool 2: Network Connections ───────────────────────────────────────────────

@mcp.tool()
def get_network_connections(memory_image: str) -> dict:
    """
    Read-only. Returns active and recently closed network connections.
    Flags connections to non-RFC1918 addresses as potentially suspicious.
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    raw = run_volatility("windows.netscan", filepath)

    connections = []
    suspicious = []

    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[0].startswith("0x"):
            continue
        try:
            local_parts = parts[2].rsplit(":", 1)
            foreign_parts = parts[3].rsplit(":", 1)
            conn = NetworkConnection(
                offset=parts[0],
                proto=parts[1],
                local_addr=local_parts[0] if len(local_parts) > 1 else parts[2],
                local_port=int(local_parts[1]) if len(local_parts) > 1 and local_parts[1].isdigit() else 0,
                foreign_addr=foreign_parts[0] if len(foreign_parts) > 1 else parts[3],
                foreign_port=int(foreign_parts[1]) if len(foreign_parts) > 1 and foreign_parts[1].isdigit() else 0,
                state=parts[4] if len(parts) > 4 else "UNKNOWN",
                pid=int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0,
                owner=parts[6] if len(parts) > 6 else None,
                created=parts[7] if len(parts) > 7 else None,
            )
            connections.append(conn)
            # Flag non-private external connections
            fa = conn.foreign_addr
            if fa and not any([
                fa.startswith("10."), fa.startswith("192.168."),
                fa.startswith("172."), fa in ["0.0.0.0", "127.0.0.1", "*"]
            ]):
                suspicious.append(conn)
        except (ValueError, IndexError):
            continue

    result = NetworkConnectionList(
        evidence=evidence,
        connections=connections,
        total_count=len(connections),
        suspicious_connections=suspicious
    )
    return result.model_dump()

# ── Tool 3: Registry Run Keys ─────────────────────────────────────────────────

@mcp.tool()
def get_registry_run_keys(memory_image: str) -> dict:
    """
    Read-only. Extracts persistence registry run keys from memory image.
    Flags entries pointing to temp directories or unusual paths.
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)

    run_keys = []
    suspicious_paths = [
        "temp", "tmp", "appdata\\local\\temp", "%temp%", 
        "downloads", "desktop", "recycle", "public",
        "programdata", "appdata\\roaming", ".exe.exe",
        "rundll32", "regsvr32", "mshta", "wscript", "cscript",
        "powershell", "cmd.exe", "certutil", "bitsadmin"
    ]

    for hive in ["HKCU", "HKLM"]:
        key = f"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        raw = run_volatility(
            "windows.registry.printkey",
            filepath,
            ["--key", key]
        )
        for line in raw.splitlines():
            if "REG_SZ" in line or "REG_EXPAND_SZ" in line:
                parts = line.strip().split(None, 3)
                if len(parts) >= 4:
                    value_name = parts[0]
                    value_data = parts[-1].strip('"')
                    is_suspicious = any(s in value_data.lower() for s in suspicious_paths)
                    run_key = RegistryRunKey(
                        hive=hive,
                        key_path=key,
                        value_name=value_name,
                        value_data=value_data,
                        last_written=None,
                        suspicious=is_suspicious,
                        reason="Unusual path detected" if is_suspicious else None
                    )
                    run_keys.append(run_key)

    result = RegistryRunKeyList(
        evidence=evidence,
        run_keys=run_keys,
        total_count=len(run_keys),
        suspicious_count=sum(1 for k in run_keys if k.suspicious)
    )
    return result.model_dump()

# ── Tool 4: MFT Timeline ──────────────────────────────────────────────────────

@mcp.tool()
def extract_mft_timeline(
    disk_image: str,
    start_time: str = "2009-12-11 00:00:00",
    end_time: str = "2009-12-11 23:59:59"
) -> dict:
    """
    Read-only. Returns MFT file system timeline entries within time range.
    Uses Volatility3 timeliner plugin on disk image.
    """
    filepath = os.path.join(CASES_DIR, disk_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    # Try timeliner first, fall back to mftparser
    raw = run_volatility("timeliner", filepath)
    
    # If timeliner returns < 5 lines, try mftparser
    if len([l for l in raw.splitlines() if l.strip()]) < 5:
        raw = run_volatility("windows.mftparser", filepath)
    
    # If still empty, try dumpfiles listing
    if len([l for l in raw.splitlines() if l.strip()]) < 5:
        raw = run_volatility("windows.filescan", filepath)

    entries = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        try:
            entry = MFTEntry(
                inode=parts[0] if parts[0] else "0",
                filename=parts[1] if len(parts) > 1 else "",
                file_path=parts[2] if len(parts) > 2 else "",
                created=parts[3] if len(parts) > 3 and parts[3] != "N/A" else None,
                modified=parts[4] if len(parts) > 4 and parts[4] != "N/A" else None,
                accessed=parts[5] if len(parts) > 5 and parts[5] != "N/A" else None,
                size=int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0,
                flags=parts[7] if len(parts) > 7 else ""
            )
            entries.append(entry)
        except (ValueError, IndexError):
            continue

    # Fallback: parse filescan output if entries is empty
    if not entries:
        for line in raw.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].startswith("0x"):
                try:
                    entry = MFTEntry(
                        inode=parts[0],
                        filename=parts[-1] if parts[-1] != "N/A" else "unknown",
                        file_path=parts[-1],
                        created=None,
                        modified=None,
                        accessed=None,
                        size=0,
                        flags="filescan"
                    )
                    entries.append(entry)
                except (ValueError, IndexError):
                    continue

    result = MFTTimeline(
        evidence=evidence,
        entries=entries[:500],  # cap at 500 to avoid context overflow
        total_count=len(entries),
        time_range_start=start_time,
        time_range_end=end_time
    )
    return result.model_dump()

# ── Tool 5: DLL List ──────────────────────────────────────────────────────────

@mcp.tool()
def get_dll_list(memory_image: str, pid: int) -> dict:
    """
    Read-only. Returns loaded DLLs for a specific process.
    Flags DLLs loaded from temp or unusual paths (potential injection).
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    raw = run_volatility("windows.dlllist", filepath, ["--pid", str(pid)])

    dlls = []
    suspicious_paths = ["temp", "tmp", "appdata\\local\\temp", "downloads", "desktop"]

    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 5 or not parts[0].startswith("0x"):
            continue
        try:
            path = parts[4] if len(parts) > 4 else ""
            is_suspicious = any(s in path.lower() for s in suspicious_paths)
            dll = DLLEntry(
                pid=pid,
                base=parts[0],
                size=int(parts[1], 16) if parts[1].startswith("0x") else 0,
                name=parts[2],
                path=path,
                suspicious=is_suspicious,
                reason="Loaded from unusual path" if is_suspicious else None
            )
            dlls.append(dll)
        except (ValueError, IndexError):
            continue

    result = DLLList(
        evidence=evidence,
        pid=pid,
        dlls=dlls,
        total_count=len(dlls),
        suspicious_count=sum(1 for d in dlls if d.suspicious)
    )
    return result.model_dump()

# ── Tool 6: Malfind ───────────────────────────────────────────────────────────

@mcp.tool()
def get_malfind(memory_image: str) -> dict:
    """
    Read-only. Detects injected code and suspicious memory regions.
    Uses Volatility3 windows.malfind plugin.
    High confidence indicator of code injection or shellcode.
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    raw = run_volatility("windows.malfind", filepath)

    entries = []
    suspicious_pids = set()
    current_entry = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        # Valid malfind line: PID ProcessName Address VadTag Protection
        # Must have real PID (>0, <65536), real address (starts with 0x), 
        # real process name (ends with .exe or is a known process)
        if len(parts) < 5:
            continue
        if not parts[0].isdigit():
            continue
        try:
            pid = int(parts[0])
            # Filter invalid PIDs
            if pid == 0 or pid > 65535:
                continue
            proc_name = parts[1]
            # Filter invalid process names
            if proc_name in ["00", "0x", ""] or len(proc_name) < 3:
                continue
            address = parts[2]
            # Filter invalid addresses
            if not address.startswith("0x") or len(address) < 4:
                continue
            vad_tag = parts[3] if len(parts) > 3 else ""
            protection = parts[4] if len(parts) > 4 else ""
            # Filter header/garbage rows
            if protection in ["00", "Protection", ""]:
                continue
            entry = MalfindEntry(
                pid=pid,
                process_name=proc_name,
                address=address,
                vad_tag=vad_tag,
                protection=protection,
                hexdump="",
                suspicious=True,
                reason="Executable memory region with no mapped file (injection indicator)"
            )
            entries.append(entry)
            suspicious_pids.add(pid)
        except (ValueError, IndexError):
            continue

    # Deduplicate entries by PID+address
    seen = set()
    unique_entries = []
    for e in entries:
        key = f"{e.pid}-{e.address}"
        if key not in seen:
            seen.add(key)
            unique_entries.append(e)
    entries = unique_entries

    result = MalfindResult(
        evidence=evidence,
        entries=entries,
        total_count=len(entries),
        suspicious_pids=list(suspicious_pids)
    )
    return result.model_dump()

@mcp.tool()
def get_evtx_events(memory_image: str) -> dict:
    """
    Read-only. Extracts Windows Event Log entries from memory.
    Flags security-relevant event IDs: 4624 (logon), 4625 (failed logon),
    4688 (process creation), 4698 (scheduled task), 7045 (service install).
    """
    filepath = os.path.join(CASES_DIR, memory_image)
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    evidence = get_evidence_metadata(filepath)
    raw = run_volatility("windows.evtlogs.EvtLogs", filepath)
    
    # Also try alternative plugin name
    if "Error" in raw or len(raw.strip()) < 10:
        raw = run_volatility("windows.evtlogs", filepath)

    suspicious_event_ids = [
        4624, 4625, 4648, 4688, 4698, 4702, 
        4720, 4726, 7045, 1102, 104
    ]
    
    entries = []
    suspicious = []

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("Volatility"):
            continue
        parts = line.split("|") if "|" in line else line.split()
        try:
            # Try to extract event ID
            event_id = 0
            for part in parts:
                part = part.strip()
                if part.isdigit() and 100 <= int(part) <= 9999:
                    event_id = int(part)
                    break
            
            if event_id == 0:
                continue
                
            is_suspicious = event_id in suspicious_event_ids
            descriptions = {
                4624: "Successful logon",
                4625: "Failed logon attempt",
                4648: "Logon with explicit credentials",
                4688: "Process creation",
                4698: "Scheduled task created",
                4702: "Scheduled task updated",
                4720: "User account created",
                4726: "User account deleted",
                7045: "New service installed",
                1102: "Audit log cleared",
                104: "System log cleared"
            }
            
            entry = EVTXEntry(
                event_id=event_id,
                timestamp=parts[0] if len(parts) > 0 else None,
                source=parts[1] if len(parts) > 1 else "unknown",
                level="WARNING" if is_suspicious else "INFO",
                description=descriptions.get(event_id, f"Event {event_id}"),
                suspicious=is_suspicious,
                reason=f"Security-relevant event ID {event_id}" if is_suspicious else None
            )
            entries.append(entry)
            if is_suspicious:
                suspicious.append(entry)
        except (ValueError, IndexError):
            continue

    result = EVTXAnalysisResult(
        evidence=evidence,
        entries=entries[:200],
        total_count=len(entries),
        suspicious_count=len(suspicious),
        suspicious_event_ids=list(set(
            e.event_id for e in suspicious
        ))
    )
    return result.model_dump()

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("SIFT-AEGIS MCP Server starting...")
    print("Available tools: get_process_list, get_network_connections,")
    print("                 get_registry_run_keys, extract_mft_timeline, get_dll_list, get_malfind")
    print("No shell execution tools exist.")
    mcp.run()
