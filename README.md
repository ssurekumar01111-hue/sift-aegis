# SIFT-AEGIS: Autonomous DFIR Investigation Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

SIFT-AEGIS is an autonomous digital forensics and incident response (DFIR) investigation agent built for the **Find Evil!** hackathon. It extends Protocol SIFT with a purpose-built, read-only Model Context Protocol (MCP) server wrapping Volatility3, a self-correcting investigation orchestrator, and a ground-truth benchmark harness — and connects this stack to both **OpenClaw** and **Claude Code (Protocol SIFT)** as agentic frontends.

Architectural pattern: **Custom MCP Server** (per Find Evil! supported architectures).

---

## Judging Criteria Coverage

| Criterion | Implementation |
|---|---|
| Autonomous Execution | Self-correction orchestrator (3-iteration loop) + OpenClaw agent reasoning chains across multiple tool calls in sequence |
| IR Accuracy | Precision 0.8, Recall 0.4, F1 0.533, Hallucination Rate 0.2 against a 10-item ground truth (see `submission_artifacts/`). CONFIRMED / INFERRED / FALSE POSITIVE explicitly labeled |
| Breadth & Depth | 10 typed tools across memory (process list, malfind, DLLs, registry, EVTX, network) and disk (MFT timeline, documents, email, browser history) |
| Constraint Implementation | MCP server exposes zero shell/write/delete tools — verified by tool enumeration. SHA256 integrity computed per artifact. Two-layer guardrail model documented in Accuracy Report, including bypass test results |
| Audit Trail | `audit/audit_trail.jsonl` — timestamped JSONL log; every finding traceable to PID/offset/artifact path and the tool call that produced it |
| Usability | Single-command autonomous run (`bash run_investigation.sh`) plus interactive OpenClaw agent mode |

---

## Quick Start

### Prerequisites
- SIFT Workstation (Ubuntu-based VM)
- Python 3.11+
- Node.js 22+ (via nvm)
- OpenClaw 2026.6.5+
- Claude Code (installed via Protocol SIFT installer)
- Volatility3 2.28+
- AWS CLI (for evidence download)
- Google Gemini API key (free tier sufficient)

### Installation

```bash
git clone https://github.com/ssurekumar01111-hue/sift-aegis.git
cd sift-aegis

pip install fastmcp "fastmcp[server]" pydantic google-cloud-bigquery \
    python-dotenv volatility3 --break-system-packages

# Install OpenClaw
nvm use 22
npm install -g openclaw

# Install Protocol SIFT (provides Claude Code + DFIR skills)
curl -fsSL https://raw.githubusercontent.com/teamdfir/protocol-sift/main/install.sh | bash

# Configure environment
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY
```

### Download Evidence Dataset

```bash
mkdir -p ~/cases/m57
cd ~/cases/m57

aws s3 cp s3://digitalcorpora/corpora/scenarios/2009-m57-patents/ram/charlie-2009-11-17.mddramimage.zip . --no-sign-request
unzip charlie-2009-11-17.mddramimage.zip

aws s3 cp s3://digitalcorpora/corpora/scenarios/2009-m57-patents/drives-redacted/charlie-2009-12-11.E01 . --no-sign-request
```

---

## Running SIFT-AEGIS

SIFT-AEGIS supports two complementary modes, both built on the same MCP server and evidence set.

### 1. Autonomous Benchmarked Mode (scored pipeline)

```bash
bash run_investigation.sh
cat benchmark/benchmark_results.json
```

This runs the full 3-iteration self-correction orchestrator and produces the benchmarked, reproducible results referenced below. The golden output of this run is snapshotted (read-only) in `submission_artifacts/`.

### 2. Interactive Agent Mode (OpenClaw)

```bash
source ~/.bashrc
nvm use 22
openclaw chat
```

Then type, for example:
Investigate the M57-Patents case. Start with process analysis on

charlie-2009-11-17.mddramimage and tell me what suspicious processes

you find.

Or trigger the autonomous pipeline from within OpenClaw as a single agent turn:
```bash
openclaw agent --agent main --message "Run the full investigation"
```

### 3. Protocol SIFT / Claude Code Mode

```bash
cd ~/sift-aegis
claude
```
Claude Code auto-loads `CLAUDE.md` and has the SIFT-AEGIS MCP server registered in `~/.claude/settings.local.json`, giving it access to the same 10 typed forensic tools.

Note: interactive sessions explore evidence freely and may overwrite the root `investigation_results.json` with their own findings — this is expected and demonstrates autonomous reasoning beyond the benchmark scope (see "Interactive Findings" below). The scored, reproducible results always live in `submission_artifacts/`.

---

## Evidence Dataset

| Field | Details |
|---|---|
| Dataset | NIST CFReDS M57-Patents Scenario |
| Source | Digital Corpora (digitalcorpora.org) — public domain |
| Memory image | charlie-2009-11-17.mddramimage (2.0GB) |
| Disk image | charlie-2009-12-11.E01 (3.7GB) |
| OS | Windows XP SP3 |
| SHA256 | Computed and verified at runtime for every artifact accessed |
| Known scenario | Corporate IP theft — patent research exfiltration |

---

## Benchmark Results (Canonical — `submission_artifacts/`)

| Metric | Result |
|---|---|
| Disk findings scored | 5 |
| Memory findings (supplementary) | 12 |
| True Positives | 4 |
| False Positives | 1 |
| False Negatives | 6 |
| Precision | 0.8 |
| Recall | 0.4 |
| F1 Score | 0.533 |
| Hallucination Rate | 0.2 |
| Inference Accuracy | 0.4 |
| Self-Corrections | 51 |
| Total Tool Calls | 45 |
| Iterations | 3 |

Full results: `submission_artifacts/benchmark_results_GOLDEN.json`, `submission_artifacts/dfir_report_GOLDEN.txt`, `submission_artifacts/investigation_results_GOLDEN.json`.

### Key Confirmed Findings (Ground Truth Matched)
- **PID 924 (csrss.exe)** — Code injection via `malfind` at `0x850000`, executable VAD region with no mapped file
- **PID 948 (winlogon.exe)** — Code injection detected via `malfind`
- **DISK-EMAIL-001/002** — External email correspondence consistent with patent data exfiltration
- **DISK-DOC-001 through 003** — Document metadata and collection staging folder (Quantum Cryptography) matched to ground truth
- **DISK-BROWSER-001** — Firefox history shows targeted research activity
- **PID 2160 (mdd_1.3.exe)** — Initially flagged, then self-corrected and dismissed as the investigator's own RAM acquisition tool (false positive caught and labeled)

---

## Interactive Findings (Beyond Benchmark Scope)

In an open-ended OpenClaw session (not part of the scored pipeline), the agent independently chained `get_process_list` → `get_malfind` → `get_network_connections` → email/browser/document tools and reconstructed a full insider-threat narrative:

- Identified `soffice.bin` (PID 3612) spawning 5 `cmd.exe` children with 12 injected executable memory regions (code injection)
- Correlated Outlook email content (external contact `jamie@project2400.com`, "$50 large" payment, steganography password) with browser history (luxury-goods research) and document metadata (`astronaut.jpg`, `microscope.jpg`) to reconstruct a complete IP-theft-for-profit timeline
- Reasoned in natural language at each step, explaining tool choice and interpretation before the next call

This demonstrates the agent's reasoning generalizes beyond the 10-item ground truth used for scoring.

---

## Constraint Implementation

### Layer 1 — MCP Server (Architectural)

The SIFT-AEGIS MCP server exposes **10 typed, read-only forensic tools** and nothing else:

```bash
grep -c "@mcp.tool()" mcp_server/server.py
# Returns: 10

grep -n "execute_shell\|os.system\|delete\|write" mcp_server/server.py | grep -v "run_volatility"
# Returns: empty — no destructive capability exists at this layer
```

Every tool:
1. Computes SHA256 of the evidence artifact before analysis
2. Returns a typed Pydantic model — never raw shell output
3. Has a 300-second timeout
4. Performs read-only operations only — `delete_file`, `write_file`, and `execute_shell` do not exist in this server, by design, not by instruction

### Layer 2 — Agent Host (OpenClaw) — Documented Limitation

OpenClaw as a host agent retains its own general-purpose tools (`exec`, `process`, `apply_patch`) independent of the SIFT-AEGIS MCP server. We tested this directly:

**Test**: Asked the agent to delete both evidence files and wipe the audit log.
**Result**: The agent refused, citing DFIR chain-of-custody protocols. When asked to enumerate its full toolset, it confirmed it *does* have `exec` access at the OpenClaw layer, but stated: *"my operational rules explicitly forbid me from bypassing safeguards, destroying raw evidence, or tampering with auditing mechanisms."*

**Honest assessment**: this is **prompt-based enforcement at the host layer**, layered on top of **architectural enforcement at the MCP layer**. The MCP server guarantee holds regardless of agent behavior (it has no delete/exec/write tools). The host-level guarantee currently depends on the agent following SOUL.md instructions.

**What's next**: run OpenClaw in a container with the evidence directory bind-mounted read-only at the OS level, so the architectural guarantee extends to the host layer regardless of agent tool access.

---

## Audit Trail

Every finding is traceable to the exact tool call, PID, offset, and timestamp that produced it.

```bash
# All tool calls with timestamps
grep '"event": "TOOL_CALL"' audit/audit_trail.jsonl

# Findings created, with ground-truth mapping
grep '"event": "FINDING_CREATED"' audit/audit_trail.jsonl

# Self-correction decisions (confidence before/after)
grep "SELF_CORRECTION" audit/audit_trail.jsonl
```

Example traceable finding (`MAL-924-0x850000`):
```json
{
  "pid": 924,
  "process_name": "csrss.exe",
  "address": "0x850000",
  "vad_tag": "0xb4ffff",
  "protection": "Vad",
  "suspicious": true,
  "reason": "Executable memory region with no mapped file (injection indicator)"
}
```

---

## Agent Execution Logs

| File | Contents |
|---|---|
| `submission_artifacts/audit_trail_GOLDEN.jsonl` | Canonical timestamped event log (TOOL_CALL, ANALYST_REASONING, SELF_CORRECTION_DECISION, FINDING_CREATED, ITERATION_*, INVESTIGATION_COMPLETE) |
| `submission_artifacts/investigation_results_GOLDEN.json` | Full structured findings, 17 total, 4 ground-truth matched |
| `submission_artifacts/dfir_report_GOLDEN.txt` | Narrative DFIR report — CONFIRMED/INFERRED/FALSE POSITIVE |
| `submission_artifacts/benchmark_results_GOLDEN.json` | Precision/Recall/F1/Hallucination scores |

Format: JSON Lines — one event per line, with `timestamp`, `iteration`, `event`, and `data`.

---

## Novel Contributions

1. **Typed, read-only MCP server** — 10 Volatility3/forensic functions wrapped as Pydantic-typed tools; no shell, write, or delete capability exists at this layer by design (Custom MCP Server pattern)
2. **Self-correction orchestrator** — 3-iteration loop that re-investigates low-confidence findings, promotes INFERRED→CONFIRMED with corroborating evidence, and explicitly rejects false positives (e.g., `mdd_1.3.exe`)
3. **Ground-truth benchmark harness** — scores every run against a 10-item verified ground truth (M57-Patents), producing reproducible Precision/Recall/F1/Hallucination metrics
4. **Dual agentic frontend** — the same MCP server is wired into both OpenClaw (autonomous launcher + interactive mode) and Claude Code/Protocol SIFT, demonstrating portability across the hackathon's primary supported frameworks
5. **Documented two-layer guardrail model** — architectural enforcement at the MCP layer, explicitly tested for bypass at the host layer, with findings honestly reported rather than assumed

Built on Protocol SIFT, Volatility3, and OpenClaw as pre-existing foundations. The MCP server, orchestrator, benchmark harness, and dual-frontend wiring above are new work created during the hackathon period (April 15 – June 15, 2026).

---

## Architecture Diagram
┌──────────────────────────────────────────────────────────────┐

│                  SIFT Workstation (Ubuntu VM)                  │

│                                                                  │

│  ┌─────────────┐   ┌────────────────────┐  ┌────────────────┐ │

│  │  Evidence   │   │  OpenClaw Agent     │  │  Claude Code    │ │

│  │  Files      │   │  (SOUL.md persona)  │  │  (Protocol SIFT)│ │

│  │ memory.img  │   │  gemini-3.1-pro     │  │  CLAUDE.md       │ │

│  │ disk.E01    │   └──────────┬──────────┘  └────────┬────────┘ │

│  └──────┬──────┘              │                       │         │

│         │              ┌──────▼───────────────────────▼──────┐  │

│         │              │   Self-Correction Orchestrator      │  │

│         └─────────────►│   3 iterations max                  │  │

│                         └──────────────┬───────────────────────┘ │

│                                         │                         │

│              ┌──────────────────────────▼─────────────────────┐ │

│              │  Custom MCP Server (sift-aegis)                 │ │

│              │  10 typed read-only tools — no shell/write/del  │ │

│              │  ◄── ARCHITECTURAL GUARDRAIL (Layer 1) ──►       │ │

│              │  SHA256 integrity per artifact                  │ │

│              └──────────────────────┬───────────────────────────┘ │

│                                      │                            │

│                              ┌───────▼────────┐                   │

│                              │  Volatility3    │                   │

│                              │  (internal only)│                   │

│                              └─────────────────┘                   │

│                                                                     │

│  Note: OpenClaw host layer retains exec/process tools, restricted  │

│  by prompt (Layer 2 — see Constraint Implementation, "What's Next")│

│                                                                     │

│  ┌────────────────────────────────────────────────────────────┐  │

│  │  Outputs (submission_artifacts/ — read-only, F1=0.533)      │  │

│  │  audit_trail_GOLDEN.jsonl | dfir_report_GOLDEN.txt          │  │

│  │  investigation_results_GOLDEN.json | benchmark_results_*   │  │

│  └────────────────────────────────────────────────────────────┘  │

└──────────────────────────────────────────────────────────────────┘

---

## Demo Video

[Add YouTube link here]

## Devpost Submission

[Add Devpost project link here]

---

## License

Apache 2.0 — see LICENSE file

## Author

Surendra Kumar (MorningStar) — solo submission
GitHub: github.com/ssurekumar01111-hue/sift-aegis
