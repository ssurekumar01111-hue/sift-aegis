# SIFT-AEGIS: Autonomous DFIR Investigation Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

SIFT-AEGIS is an autonomous digital forensics and incident response (DFIR) investigation agent built for the **Find Evil!** hackathon. It extends Protocol SIFT with a purpose-built, read-only Model Context Protocol (MCP) server wrapping Volatility3, a self-correcting investigation orchestrator, and a ground-truth benchmark harness — and connects this stack to both **OpenClaw** and **Claude Code (Protocol SIFT)** as agentic frontends.

Architectural pattern: **Custom MCP Server** (per Find Evil! supported architectures).

---

## Judging Criteria Coverage

| Criterion | Implementation |
|---|---|
| Autonomous Execution | Self-correction orchestrator (3-iteration loop) + OpenClaw agent reasoning chains across multiple tool calls in sequence |
| IR Accuracy | Precision 1.0, Recall 1.0, F1 1.0, Hallucination Rate 0.0 against a 10-item ground truth (see `submission_artifacts/`). CONFIRMED / INFERRED / FALSE POSITIVE explicitly labeled |
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
Investigate the M57-Patents case. Start with process analysis on charlie-2009-11-17.mddramimage and tell me what suspicious processes you find.

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
| Disk findings scored | 9 |
| Memory findings (supplementary) | 12 |
| True Positives | 10 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 1.0 |
| Recall | 1.0 |
| F1 Score | 1.0 |
| Hallucination Rate | 0.0 |
| Inference Accuracy | 1.0 |
| Self-Corrections | 59 |
| Total Tool Calls | 36 |

Full results: `submission_artifacts/benchmark_results_GOLDEN.json`, `submission_artifacts/dfir_report_GOLDEN.txt`, `submission_artifacts/investigation_results_GOLDEN.json`.

---

## Interactive Findings (Beyond Benchmark Scope)

In an open-ended OpenClaw session (not part of the scored pipeline), the agent independently chained `get_process_list` → `get_malfind` → `get_network_connections` → email/browser/document tools and reconstructed a full insider-threat narrative.

This demonstrates the agent's reasoning generalizes beyond the 10-item ground truth used for scoring.

---

## Constraint Implementation

### Layer 1 — MCP Server (Architectural)

The SIFT-AEGIS MCP server exposes **10 typed, read-only forensic tools** and nothing else.

Every tool:
1. Computes SHA256 of the evidence artifact before analysis
2. Returns a typed Pydantic model — never raw shell output
3. Has a 300-second timeout
4. Performs read-only operations only — `delete_file`, `write_file`, and `execute_shell` do not exist in this server, by design, not by instruction.

### Layer 2 — Agent Host (OpenClaw) — Documented Limitation

OpenClaw as a host agent retains its own general-purpose tools (`exec`, `process`, `apply_patch`) independent of the SIFT-AEGIS MCP server.

**Honest assessment**: this is **prompt-based enforcement at the host layer**, layered on top of **architectural enforcement at the MCP layer**. The MCP server guarantee holds regardless of agent behavior (it has no delete/exec/write tools). The host-level guarantee currently depends on the agent following SOUL.md instructions.

**What's next**: run OpenClaw in a container with the evidence directory bind-mounted read-only at the OS level, so the architectural guarantee extends to the host layer regardless of agent tool access.

---

## Audit Trail

Every finding is traceable to the exact tool call, PID, offset, and timestamp that produced it.

---

## Canonical Benchmark Evidence

The files in `submission_artifacts/` are the verified, reproducible
output of `python3 sift_aegis.py` (F1=1.0, Precision=1.0, Recall=1.0,
Hallucination=0.0). These are the canonical results referenced in the
Accuracy Report and Devpost submission.

Note: `investigation_results.json` at the project root may be
overwritten by interactive agent sessions (OpenClaw/Claude Code) that
explore the case data freely. This is expected — interactive sessions
demonstrate autonomous reasoning beyond the benchmark scope. The golden
artifacts in `submission_artifacts/` always reflect the scored,
reproducible pipeline run and are read-only (chmod 444).

---

## License

Apache 2.0 — see LICENSE file

## Author

Surendra Kumar (MorningStar) — solo submission
GitHub: github.com/ssurekumar01111-hue/sift-aegis
