# 3-minute demo script
Pre-flight: `NOGAIN_BRIEFING_SECONDS=30`, API + UI running, seeded data, backup video ready. Mock or live: say which.
1. **(0:00) Hook, 15s.** "Your notes, grades and CV never leave your control."
2. **(a) Notes -> plan, 40s.** Study tab: upload `cs101_algorithms.md` (course CS101) -> 7-day plan -> flashcards -> quiz; answer one wrong.
3. **(c) Memory, 25s.** Memory tab shows "Struggled with ... in CS101". Chat: "What should I focus on?" -> reply cites it. Delete a memory to show control.
4. **(b) Always-on, 20s.** Briefings tab: the scheduler has already fired a briefing mentioning the weak topic and tomorrow's deadline.
5. **(d) Attack, 60s.** Security tab -> "Analyze malicious job posting". Show posting text. Result: the key read and the POST to evil.example are BLOCKED; open the audit log. Then show the sandbox side: `./scripts/openshell_demo.sh` output and `openshell logs`.
6. **(e) Nebius, 20s.** Same run against the deployed endpoint URL; Nemotron model name visible in the audit log.
7. **Close, 10s.** Two layers (OpenShell + app policy), local memory, open models.
Backup: pre-recorded video of steps 2-6; `data/home` is seeded and the mock LLM needs no network.
Honesty line for judges: the injected instruction is obeyed by a *simulated gullible model* in mock mode; with the live model the block still holds either way.
