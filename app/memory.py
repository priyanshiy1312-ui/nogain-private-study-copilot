"""Long-term memory: vector-searchable facts the student can inspect and delete."""
import time
from . import embed, store


def add(kind: str, text: str) -> int:
    q = embed.embed(text)
    near = store.vec_search("memories", q, k=1)
    if near and near[0]["score"] > 0.92:        # de-duplicate near-identical memories
        return near[0]["id"]
    return store.execute("INSERT INTO memories(ts,kind,text,emb) VALUES(?,?,?,?)",
                         (time.time(), kind, text, q.tobytes()))


def recall(query: str, k: int = 4):
    return store.vec_search("memories", embed.embed(query), k=k)


def list_all(kind=None):
    rows = store.query("SELECT id,ts,kind,text FROM memories" + (" WHERE kind=?" if kind else "") + " ORDER BY id DESC",
                       (kind,) if kind else ())
    return rows


def delete(mem_id: int):
    store.execute("DELETE FROM memories WHERE id=?", (mem_id,))
