# NoGain: private Student Study & Career Copilot
Nebius x NVIDIA Global AI Hackathon, Personal AI track. Always-on private assistant: memory, study engine,
career tailoring, and every action sandboxed and audited (NVIDIA OpenShell + Nemotron on Nebius).

## Quick start (works with zero keys: mock LLM)
Windows: do everything inside **WSL2 Ubuntu** (VS Code Remote-WSL).
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q tests          # 9 tests, all should pass
cp .env.example .env               # NOGAIN_LLM=mock by default
./scripts/run_api.sh               # terminal 1  -> http://localhost:8000/docs
./scripts/run_ui.sh                # terminal 2  -> http://localhost:8501
```
**Go live (Nemotron on Nebius Token Factory):** set `NOGAIN_LLM=live` and `NEBIUS_API_KEY` in `.env`, then
`curl -H "Authorization: Bearer $NEBIUS_API_KEY" https://api.tokenfactory.nebius.com/v1/models` and put the
exact Nemotron IDs into `NOGAIN_MODEL` / `NOGAIN_FAST_MODEL`.

## Status: what is verified vs not
| Area | Status |
|---|---|
| Ingest, memory (view/delete), chat, 7-day plan, flashcards, quiz, briefing scheduler, career tailoring w/ grounding check, approvals, audit log, privacy redaction | **Built and tested in mock mode** (pytest) |
| App-level policy engine (same `policy.yaml` subset OpenShell uses) | **Built and tested**; blocks the injection demo at fs + network layers |
| Live Nemotron on Nebius | **Untested here** (no key/network). First task: smoke test. Reasoning models may return empty `content`; client already falls back to `reasoning_content` and uses JSON, not native tool calls |
| OpenShell sandbox run (`scripts/openshell_demo.sh`) | **Untested**. Commands come from the docs; flag combos and the `sandbox/Dockerfile` base image are unverified. Windows+WSL2 is "Experimental" upstream and needs Landlock (Linux >= 6.2): run `scripts/wsl_check.sh` first |
| Importing OpenShell logs into the UI audit panel | **Not built** (log format not yet inspected; OCSF JSON export exists). Task for Person B |
| Nebius Serverless deploy (`scripts/deploy_nebius.sh`) | **Untested**; flags from the docs. OpenShell itself probably can't run inside a Serverless container, so the deployed app uses the app-level policy engine |
| Hermes Agent skill spike, local-model privacy routing, Chroma | **Not built** (stretch) |

## Layout
`app/` core (FastAPI) · `ui/` Streamlit · `policy/` OpenShell policy template + app policy · `sandbox/` image + in-sandbox demo ·
`scripts/` run/deploy · `data/home/` seeded demo data (notes, CV, postings) · `docs/` architecture, threat model, demo script, plan, pitch.

## Two security layers (be precise in the pitch)
1. **OpenShell** (kernel/proxy): filesystem allowlist (Landlock) + egress allowlist. Hot-reloadable network rules.
   Set `enforcement: enforce`, because the default `audit` only logs.
2. **App layer** (`policy_engine.py`, `tools.py`): per-tool toggles, human approval, taint rule, audit. OpenShell
   does not provide per-tool toggles, so this layer is ours.

## OpenShell demo (hour 2 gate)
```bash
./scripts/wsl_check.sh && ./scripts/openshell_demo.sh   # prints [ALLOWED]/[BLOCKED] then `openshell logs`
```
Verify first: `openshell sandbox create --help`. Docs: docs.nvidia.com/openshell (policy schema reference).
Policy note: `binaries` must be the interpreter's REAL path (`/usr/bin/python3.12`, not the symlink).
