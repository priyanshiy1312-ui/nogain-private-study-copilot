# Architecture and trust boundaries
```mermaid
flowchart LR
  subgraph TB1["Trust boundary 1: student's machine / Nebius endpoint"]
    UI["Streamlit UI"] <--> API["FastAPI core: orchestrator,<br/>approval gate, taint rule"]
    SCH["Scheduler daemon"] --> API
    API <--> MEM[("SQLite + local embeddings<br/>memory, notes, tracker, audit")]
    API --> PR["Privacy router (redaction)"]
  end
  subgraph TB2["Trust boundary 2: OpenShell sandbox + policy.yaml"]
    W["Agent worker / tools"] --- FS["approved folders only (Landlock)"]
  end
  PR --> W
  W -->|allowlisted| NEB["Nebius Token Factory: Nemotron"]
  W -->|allowlisted, read-only| JOB["approved job sites"]
  W -.->|DENIED + logged| EVIL["evil.example"]
  W --> AUD[("Audit log")] --> UI
```
Untrusted content (job postings) enters only as `<untrusted_data>`; the model proposes JSON actions, the core
executes them via `tools.call` (enabled -> taint rule -> fs/net policy -> approval -> execute -> audit).
In this repo the app-layer engine runs in-process; the OpenShell sandbox is exercised by `sandbox/sandbox_demo.py`.
Moving the real worker fully inside the sandbox is Person B's hour 8-12 task.
