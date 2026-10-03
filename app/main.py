"""FastAPI core. Endpoints are the API contract between UI (C), agent core (A) and security/infra (B)."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from . import agent, audit, career, config, ingest, llm, memory, privacy, scheduler, store, study, tools
from .policy_engine import PolicyDenied


@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="NoGain", lifespan=lifespan)


@app.exception_handler(PolicyDenied)
async def _denied(_, e: PolicyDenied):
    audit.log("core", "request", "-", "BLOCKED", e.layer, {"reason": e.reason})
    return JSONResponse(status_code=403, content={"blocked": True, "layer": e.layer, "reason": e.reason})


@app.exception_handler(ValueError)
async def _bad(_, e: ValueError):
    return JSONResponse(status_code=502, content={"error": str(e)})


class IngestReq(BaseModel):
    path: str
    course: str


class ChatReq(BaseModel):
    message: str
    session_id: str = "default"


class CourseReq(BaseModel):
    course: str
    n: int = 5


class ResultReq(BaseModel):
    course: str
    topic: str
    correct: bool


class PostingReq(BaseModel):
    source: str = "jobs/malicious_posting.txt"
    simulate_compromised: bool = False
    taint_rule: bool | None = None   # None = use app_policy.yaml; False = let the network layer do the blocking


class TailorReq(BaseModel):
    posting_text: str


class AppReq(BaseModel):
    company: str
    role: str
    status: str = "saved"
    notes: str = ""


@app.get("/health")
def health():
    return {"ok": True, "llm_mode": config.LLM_MODE, "model": config.MODEL, "home": str(config.HOME)}


@app.post("/ingest")
def do_ingest(r: IngestReq):
    return {"chunks": ingest.ingest_path(r.path, r.course), "course": r.course}


@app.get("/courses")
def courses():
    return ingest.courses()


@app.post("/chat")
def chat(r: ChatReq):
    safe = privacy.route(r.message)
    mems = memory.recall(safe["text"], 4)
    notes = ingest.search(safe["text"], k=2)
    hist = store.query("SELECT role,content FROM messages WHERE session=? ORDER BY id DESC LIMIT 6", (r.session_id,))[::-1]
    ctx = ("Relevant memories:\n" + "\n".join(f"- {m['text']}" for m in mems if m["score"] > 0.05)
           + "\n\nRelevant notes:\n" + "\n".join(n["text"][:300] for n in notes)
           + f"\n\nStudent: {safe['text']}")
    reply = llm.complete("chat", "You are NoGain, a private study and career copilot. Be concise.",
                         ctx, history=hist, route=safe["route"])
    store.execute("INSERT INTO messages(ts,session,role,content) VALUES(?,?,?,?)", (time.time(), r.session_id, "user", safe["text"]))
    store.execute("INSERT INTO messages(ts,session,role,content) VALUES(?,?,?,?)", (time.time(), r.session_id, "assistant", reply))
    try:  # long-term memory extraction (cheap model); never block the reply on it
        for f in llm.complete_json("extract_memory", 'Extract durable facts about the student as JSON [{"kind":"weakness|goal|fact","text":""}]; [] if none.',
                                   safe["text"], model=config.FAST_MODEL):
            memory.add(f.get("kind", "fact"), f["text"])
    except Exception:
        pass
    return {"reply": reply, "memories_used": [m["text"] for m in mems if m["score"] > 0.05],
            "route": safe["route"], "redactions": safe["redactions"],
            "model": "mock" if config.LLM_MODE == "mock" else config.MODEL}


@app.get("/memories")
def memories():
    return memory.list_all()


@app.delete("/memories/{mem_id}")
def del_memory(mem_id: int):
    memory.delete(mem_id)
    audit.log("user", "memory", mem_id, "DELETED", "ui")
    return {"deleted": mem_id}


@app.post("/study/plan")
def study_plan(r: CourseReq):
    return study.plan(r.course, 7)


@app.post("/study/flashcards")
def study_cards(r: CourseReq):
    return study.flashcards(r.course, r.n)


@app.post("/study/quiz")
def study_quiz(r: CourseReq):
    return study.quiz(r.course, r.n)


@app.post("/study/result")
def study_result(r: ResultReq):
    return {"memory_id": study.record_result(r.course, r.topic, r.correct)}


@app.get("/briefings")
def briefings():
    return store.query("SELECT * FROM briefings ORDER BY id DESC LIMIT 10")


@app.post("/briefing/now")
def briefing_now():
    return {"text": scheduler.make_briefing()}


@app.get("/audit")
def get_audit(limit: int = 100):
    return audit.recent(limit)


@app.post("/jobs/analyze")
def jobs_analyze(r: PostingReq):
    return agent.analyze_posting(r.source, r.simulate_compromised, r.taint_rule)


@app.post("/career/tailor")
def career_tailor(r: TailorReq):
    return career.tailor(r.posting_text)


@app.get("/applications")
def get_apps():
    return store.query("SELECT * FROM applications ORDER BY id DESC")


@app.post("/applications")
def add_app(r: AppReq):
    return {"id": store.execute("INSERT INTO applications(ts,company,role,status,notes) VALUES(?,?,?,?,?)",
                                (time.time(), r.company, r.role, r.status, r.notes))}


@app.get("/approvals")
def approvals():
    return tools.pending()


@app.post("/approvals/{aid}/{verdict}")
def decide(aid: int, verdict: str):
    if verdict not in ("approve", "deny"):
        raise HTTPException(400, "verdict must be approve|deny")
    return tools.decide(aid, verdict == "approve")
