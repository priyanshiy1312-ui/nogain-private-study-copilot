"""Notes/PDF ingestion: read -> chunk -> embed locally -> store with course metadata."""
from pathlib import Path
from . import embed, policy_engine, store


def _read(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    return path.read_text(errors="ignore")


def chunk(text: str, size=800, overlap=100):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return [c for c in out if c.strip()]


def ingest_path(path: str, course: str) -> int:
    p = policy_engine.check_fs(path, "r")           # raises PolicyDenied outside approved folders
    store.execute("DELETE FROM chunks WHERE source=?", (p.name,))   # re-ingest = replace
    n = 0
    for i, c in enumerate(chunk(_read(p))):
        store.execute("INSERT INTO chunks(course,source,idx,text,emb) VALUES(?,?,?,?,?)",
                      (course, p.name, i, c, embed.embed(c).tobytes()))
        n += 1
    return n


def courses():
    return [r["course"] for r in store.query("SELECT DISTINCT course FROM chunks")]


def search(query: str, course=None, k=3):
    where, args = ("WHERE course=?", (course,)) if course else ("", ())
    return store.vec_search("chunks", embed.embed(query), k=k, where=where, args=args)
