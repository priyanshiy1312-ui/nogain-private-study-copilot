"""Privacy router (stub-level): redact sensitive fields before text reaches the hosted model.
Extension point: send highly sensitive requests to a small LOCAL model (e.g. via Ollama) instead."""
import re

PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"\+?\d[\d\s().-]{8,}\d"), "[PHONE]"),
    (re.compile(r"\b(?:c?gpa)\s*[:=]?\s*\d(?:\.\d+)?(?:\s*/\s*\d(?:\.\d+)?)?", re.I), "[GRADE]"),
    (re.compile(r"\b(?:scored|got|received)\s+\d{2,3}\s*%", re.I), "[GRADE]"),
]


def route(text: str):
    hits, out = [], text
    for pat, repl in PATTERNS:
        if pat.search(out):
            hits.append(repl.strip("[]"))
            out = pat.sub(repl, out)
    return {"text": out, "redactions": sorted(set(hits)),
            "route": "hosted:redacted" if hits else "hosted"}
