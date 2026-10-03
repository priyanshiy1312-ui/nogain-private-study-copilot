# One-page pitch + slide outline
**Problem.** Students juggle notes, deadlines and applications, and the AI tools that could help want their grades, CVs and emails in someone else's cloud.
**Solution.** NoGain: an always-on private copilot. It ingests your notes, builds and adapts study plans, quizzes you, remembers where you struggle, and tailors CVs and cover letters using only real experience.
**Privacy story.** Data and memory are local and viewable/deletable. Sensitive fields are redacted before any hosted call. Agent actions run under a default-deny policy (OpenShell sandbox: approved folders, allowlisted egress) plus per-tool toggles and human approval. Every tool and model call is in an audit log.
**Tech.** NVIDIA Nemotron on Nebius Token Factory, NVIDIA OpenShell, FastAPI, Streamlit, local embeddings, SQLite; deployable to Nebius Serverless.
**Impact.** Safe-by-default personal AI students can trust; same pattern works for any personal data workload.
Slides: 1 Problem · 2 Solution · 3 Architecture (trust boundaries) · 4 Privacy story · 5 Live demo · 6 Impact · 7 Future (Hermes skills, local model routing, calendar, spaced repetition).
