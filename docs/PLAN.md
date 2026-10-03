# 24h plan (3 people) and cut-lines
Roles: A agent core/AI, B security/infra, C product/UI. Everyone develops in WSL2.
| Hours | A | B | C |
|---|---|---|---|
| 0-1 | Run tests, Nebius smoke test, confirm model IDs | `wsl_check.sh`; install Docker Desktop/OpenShell | Run UI against mock |
| 1-2 | Switch to live LLM; handle empty `content` | **OpenShell gate (hour 2):** `openshell_demo.sh` works or fall back to policy engine | UI polish list |
| 2-4 | Real PDFs, chunk quality, prompts | Move worker into sandbox; policy tweaks | Chat/memory UX |
| 4 | **Sync 1** | | |
| 4-8 | Plan/quiz quality; spaced repetition (nice) | OpenShell log -> audit panel import | Plan view, audit view |
| 8 | **Sync 2** | | |
| 8-12 | Memory recall quality, seeded demo data | Nebius deploy, scheduler on endpoint | End-to-end demo run, script |
| 12 | **Sync 3: end-to-end demo works or cut skill/privacy-router** | | |
| 12-16 | Career engine tuning | Deploy hardening | UI polish, tracker |
| 16 | **Sync 4**; staggered 3h naps | | |
| 16-20 | ONE of: Hermes skill / local-model privacy route | Backup video recording | Slides, pitch |
| 20 | **Sync 5: feature freeze** | | |
| 20-24 | Bugs only | Seeded fallback | Rehearse 5+ times |
Cut-lines: OpenShell not working at hour 2 -> policy engine only; no E2E at hour 12 -> drop stretch items; Nebius deploy failing at hour 16 -> record local demo.
