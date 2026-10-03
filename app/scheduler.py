"""Always-on daemon: APScheduler fires the morning briefing (interval is short for demos)."""
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler
from . import audit, config, llm, memory, store

_sched = None


def make_briefing():
    f = config.HOME / "deadlines.json"
    deadlines = json.loads(f.read_text()) if f.exists() else []
    weak = [m["text"] for m in memory.list_all("weakness")][:3]
    u = (f"Deadlines: {deadlines}\nWeak topics: {weak}\n"
         "Write a friendly 3-sentence morning briefing for the student.")
    text = llm.complete("briefing", "You are the student's private study assistant.", u, model=config.FAST_MODEL)
    store.execute("INSERT INTO briefings(ts,text) VALUES(?,?)", (time.time(), text))
    audit.log("scheduler", "briefing", "morning", "allow", "scheduler")
    return text


def start():
    global _sched
    if _sched is None:
        _sched = BackgroundScheduler()
        _sched.add_job(make_briefing, "interval", seconds=config.BRIEFING_SECONDS, id="briefing")
        _sched.start()


def stop():
    global _sched
    if _sched:
        _sched.shutdown(wait=False)
        _sched = None
