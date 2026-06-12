# Architecture Audit

## AUDIT 1 — Project Structure

### Directory Tree
(Represented by the initial `find` command structure.)

### .py Files Purpose
- `mcp_server/server.py`: MCP Server for forensic analysis tools.
- `mcp_server/models.py`: Pydantic models for forensics results.
- `mcp_bridge.py`: Bridge between Orchestrator and MCP Server.
- `orchestrator.py`: Main investigation orchestrator (SIFT-AEGIS).
- `audit/bigquery_logger.py`: Logging.
- `benchmark/benchmark_runner.py`: Benchmarking tool.
- `sift_aegis.py`: Main entry point wrapper?
- `test_confidence_engine.py`: Test.
- `demo/demo_mode.py`: Demo.
- `test_evidence_graph.py`: Test.
- `test_malfind.py`: Test.
- `scripts/...`: Analysis scripts.
- `user_activity_timeline.py`: Timeline analysis.
- `test_nov17.py`: Test.
- `run_email_forensics.py`: Email analysis script.
- `openclaw_skill/skill.py`: Custom skill.
- `patch_report.py`: Report generation script.
- `reports/report_generator.py`: Report generator.
- `run_browser_forensics.py`: Browser forensics.
- `agents/...`: Agent definitions (Empty).
- `run_document_forensics.py`: Document forensics.
- `evidence_graph.py`: Graph engine.
- `incident_reconstruction.py`: Incident reconstruction engine.
- `simulate_finding_corroboration.py`: Simulation.
- `mitre_mapping_engine.py`: MITRE engine.
- `attack_chain_engine.py`: Attack chain engine.
- `replay_engine.py`: Replay engine.
- `test_malfind_fix.py`: Fix test.
- `patch_orchestrator.py`: Patch script.

## AUDIT 2 — Orchestrator Deep Read (`patch_orchestrator.py` is a patch script)
- Patch orchestrator file is not the main orchestrator, it's a script that modifies `orchestrator.py`.
- **Investigation triggered**: Not in `patch_orchestrator.py`.
- **Entry point**: `python3 patch_orchestrator.py` (assumed).

## AUDIT 3 — MCP Server Deep Read (`mcp_server/server.py`)
- **Tools**:
    - `get_process_list`: Process list from memory.
    - `get_network_connections`: Network connections from memory.
    - `get_registry_run_keys`: Persistence registry run keys.
    - `extract_mft_timeline`: MFT timeline.
    - `get_dll_list`: Loaded DLLs for a process.
    - `get_malfind`: Injected code detection.
    - `get_evtx_events`: EVTX event log analysis.
    - `extract_outlook_emails`: Read emails (JSON).
    - `analyze_browser_artifacts`: Browser history/downloads/cookies (JSON).
    - `extract_document_metadata`: Office/PDF metadata (JSON).
- **Server start**: `mcp.run()`
- **Agent connection**: Via `mcp_bridge.py`.

## AUDIT 4 — Agent Files Deep Read
- Agents in `agents/` are all 0 bytes.
- The `SIFT-AEGISOrchestrator` in `orchestrator.py` handles all logic, effectively replacing agent functionality in this version.

## AUDIT 5 — Investigation Run Flow
1. **Entry Point**: `python3 orchestrator.py` (which runs `investigate()`).
2. **Memory Analysis** (`phase_memory_analysis`): Calls MCP tools for process list, network, registry, malfind, evtx.
3. **Correlation** (`phase_correlation`): Correlates findings.
4. **Disk Correlation** (`phase_disk_correlation`): Cross-references MFT.
5. **Self-Correction** (`phase_self_correction`): Re-runs tools to verify low confidence findings.
6. **Findings**: Written to `investigation_results.json` at the end of the script.
7. **Files Produced**: `graph/evidence_graph.json`, `replay/TEST-1_replay.json` (as logged in `orchestrator.py`).

## AUDIT 6 — Current Findings Format (`evidence_graph.json`, `attack_chain.json`)
Finding object example (from `evidence_graph.json` node):
```json
{
  "id": "MEM-3908",
  "type": "Finding",
  "name": "Suspicious Process: cmd.exe",
  "confidence": 0.25,
  "metadata": {
    "category": "Suspicious Process",
    "description": "Process cmd.exe (PID 3908) has anomalous parent-child relationship"
  }
}
```

## AUDIT 7 — Tools NEVER Called
- MCP tools not called by `orchestrator.py`:
    - `extract_outlook_emails`
    - `analyze_browser_artifacts`
    - `extract_document_metadata`
