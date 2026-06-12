# SIFT-AEGIS
## Autonomous Evidence Guardian and Incident Synthesizer
### Extension of Protocol SIFT — Find Evil Hackathon 2026

---

## What SIFT-AEGIS Adds to Protocol SIFT

Protocol SIFT connects Claude Code to 200+ SIFT tools via raw shell execution.
SIFT-AEGIS adds a typed MCP layer that eliminates hallucinations and measures accuracy.

| Capability | Protocol SIFT (baseline) | SIFT-AEGIS (this project) |
|---|---|---|
| Tool execution | Raw shell → unstructured output | Typed MCP → Pydantic-validated results |
| Hallucination control | Prompt-based guidance | Architectural — impossible to hallucinate structure |
| Accuracy measurement | None | Ground truth benchmark — F1=1.0 |
| Evidence integrity | SHA256 on mount | SHA256 on every tool call |
| Audit trail | forensic_audit.log | JSONL — every finding traceable |
| Self-correction | None | 3-iteration loop with confidence scoring |
| MITRE mapping | None | ATT&CK technique on every finding |

---

## MCP Server Tools Available

These tools are registered in ~/.claude/settings.local.json.
Claude Code can call them directly without shell access.

| Tool | Purpose | Returns |
|---|---|---|
| get_process_list | Process tree with parent-child anomaly detection | ProcessListResult |
| get_network_connections | Active connections, flags external IPs | NetworkConnectionList |
| get_registry_run_keys | Persistence via Run keys | RegistryRunKeyList |
| get_malfind | Code injection / shellcode detection | MalfindResult |
| get_dll_list | Per-process DLL injection detection | DLLList |
| extract_mft_timeline | File system activity timeline | MFTTimeline |
| get_evtx_events | Windows Event Log analysis | EVTXAnalysisResult |

---

## Running an Investigation

### Automated (recommended for demo):
  bash run_investigation.sh

### Interactive (Claude Code):
  cd /home/sansforensics/sift-aegis
  claude
  # Then say: "Investigate the M57-Patents case for IP theft artifacts"

### Benchmark results:
  cat benchmark/benchmark_results.json

---

## Evidence

| File | Path | Size |
|---|---|---|
| Memory image | /home/sansforensics/cases/m57/charlie-2009-11-17.mddramimage | 2.0GB |
| Disk image | /home/sansforensics/cases/m57/charlie-2009-12-11.E01 | 3.7GB |
| Dataset | NIST CFReDS M57-Patents — public domain |
| Ground truth | ground_truth_rebuilt.json — 10 verified artifacts |

---

## Benchmark Results (M57-Patents)

| Metric | Score |
|---|---|
| Precision | 1.0 |
| Recall | 1.0 |
| F1 Score | 1.0 |
| Hallucination Rate | 0.0 |
| Self-Corrections | 59 |
| Total Tool Calls | 36 |

---

## Architecture

Evidence Files
→ Custom MCP Server (10 typed read-only tools, SHA256 verified)
→ Self-Correction Orchestrator (3 iterations, confidence scoring)
→ Ground Truth Benchmark (precision/recall/F1 vs 10 verified artifacts)
→ DFIR Report + JSONL Audit Trail
