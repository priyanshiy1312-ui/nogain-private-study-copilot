"""NoGain UI (Streamlit). Run: streamlit run ui/streamlit_app.py   (API must be running on :8000)"""
import os
import pandas as pd
import requests
import streamlit as st

API = os.environ.get("NOGAIN_API", "http://127.0.0.1:8000")
HOME = os.environ.get("NOGAIN_HOME", os.path.join(os.path.dirname(__file__), "..", "data", "home"))
st.set_page_config(page_title="NoGain", page_icon="🎓", layout="wide")


def api(method, path, **kw):
    r = requests.request(method, API + path, timeout=120, **kw)
    return r.status_code, (r.json() if r.content else None)


st.title("🎓 NoGain: private study & career copilot")
h = api("GET", "/health")[1]
st.caption(f"LLM mode: **{h['llm_mode']}** · model: `{h['model']}` · data stays in `{h['home']}`")
tabs = st.tabs(["💬 Chat", "📚 Study", "🧠 Memory", "☀️ Briefings", "💼 Career", "🛡️ Security & audit"])

with tabs[0]:
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for role, msg in st.session_state.chat:
        st.chat_message(role).write(msg)
    if prompt := st.chat_input("Ask anything about your courses…"):
        st.session_state.chat.append(("user", prompt))
        _, r = api("POST", "/chat", json={"message": prompt})
        st.session_state.chat.append(("assistant", r["reply"]))
        st.rerun()
    if st.session_state.chat:
        _, last = api("GET", "/memories")
        st.caption("Privacy router: every request is redacted before leaving the machine; see Audit for the model used.")

with tabs[1]:
    up = st.file_uploader("Upload lecture notes (.md/.txt/.pdf)")
    course = st.text_input("Course", "CS101")
    if up and st.button("Ingest"):
        os.makedirs(os.path.join(HOME, "notes"), exist_ok=True)
        dest = os.path.join(HOME, "notes", up.name)
        open(dest, "wb").write(up.getbuffer())
        st.json(api("POST", "/ingest", json={"path": f"notes/{up.name}", "course": course})[1])
    c1, c2, c3 = st.columns(3)
    if c1.button("7-day plan"):
        st.session_state.plan = api("POST", "/study/plan", json={"course": course})[1]
    if c2.button("Flashcards"):
        st.session_state.cards = api("POST", "/study/flashcards", json={"course": course})[1]
    if c3.button("Quiz"):
        st.session_state.quiz = api("POST", "/study/quiz", json={"course": course})[1]
    for d in (st.session_state.get("plan") or {}).get("days", []):
        st.markdown(f"**Day {d['day']}: {d['focus']}** ({d.get('minutes', '?')} min): " + "; ".join(d["tasks"]))
    for card in st.session_state.get("cards", []):
        with st.expander(card["front"]):
            st.write(card["back"])
    for q in st.session_state.get("quiz", []):
        ans = st.radio(q["question"], q["options"], index=None, key=f"q{q['id']}")
        if ans is not None and st.button("Check", key=f"b{q['id']}"):
            ok = q["options"].index(ans) == q["answer_index"]
            st.success("Correct") if ok else st.error(q["explanation"])
            api("POST", "/study/result", json={"course": course, "topic": q["topic"], "correct": ok})

with tabs[2]:
    for m in api("GET", "/memories")[1]:
        a, b = st.columns([8, 1])
        a.write(f"`{m['kind']}` {m['text']}")
        if b.button("🗑", key=f"m{m['id']}"):
            api("DELETE", f"/memories/{m['id']}")
            st.rerun()

with tabs[3]:
    if st.button("Fire briefing now"):
        api("POST", "/briefing/now")
    for b in api("GET", "/briefings")[1]:
        st.info(b["text"])
    st.caption("The scheduler daemon fires these automatically (NOGAIN_BRIEFING_SECONDS).")

with tabs[4]:
    posting = st.text_area("Paste a job posting", open(os.path.join(HOME, "jobs", "legit_posting.txt")).read(), height=160)
    if st.button("Tailor CV + cover letter"):
        _, t = api("POST", "/career/tailor", json={"posting_text": posting})
        st.write("**Grounded bullets** (each cites a real profile entry):")
        for b in t["bullets"]:
            st.write(f"- {b['text']}  _(source {b['source_id']})_")
        st.write(t["cover_letter"])
    st.dataframe(pd.DataFrame(api("GET", "/applications")[1]))

with tabs[5]:
    st.subheader("Prompt-injection demo")
    only_net = st.checkbox("Disable app taint-rule so the NETWORK allowlist is what blocks it", True)
    if st.button("Analyze malicious job posting"):
        _, r = api("POST", "/jobs/analyze", json={"source": "jobs/malicious_posting.txt",
                                                  "taint_rule": False if only_net else None})
        st.error(f"{r['blocked']} attempted action(s) BLOCKED")
        st.dataframe(pd.DataFrame(r["proposed_actions"]))
    st.subheader("Approval queue")
    for a in api("GET", "/approvals")[1]:
        x, y, z = st.columns([6, 1, 1])
        x.write(f"{a['tool']} {a['args']}")
        if y.button("Approve", key=f"a{a['id']}"):
            api("POST", f"/approvals/{a['id']}/approve"); st.rerun()
        if z.button("Deny", key=f"d{a['id']}"):
            api("POST", f"/approvals/{a['id']}/deny"); st.rerun()
    st.subheader("Audit log (every tool + LLM call)")
    df = pd.DataFrame(api("GET", "/audit?limit=60")[1])
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], unit="s")
        st.dataframe(df[["ts", "actor", "tool", "target", "decision", "layer"]], use_container_width=True)
    st.button("Refresh")
