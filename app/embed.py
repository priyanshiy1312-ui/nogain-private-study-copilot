"""Local, dependency-free embeddings (feature hashing). Data never leaves the machine.
Set NOGAIN_EMBED=st to use sentence-transformers instead (bake the model into the image first:
the sandbox blocks downloads)."""
import hashlib, os, re
import numpy as np

DIM = 512
_st = None


def embed(text: str) -> np.ndarray:
    global _st
    if os.environ.get("NOGAIN_EMBED") == "st":
        if _st is None:
            from sentence_transformers import SentenceTransformer
            _st = SentenceTransformer("all-MiniLM-L6-v2")
        return _st.encode(text, normalize_embeddings=True).astype(np.float32)
    toks = re.findall(r"[a-z0-9]+", text.lower())
    feats = toks + [a + "_" + b for a, b in zip(toks, toks[1:])]
    v = np.zeros(DIM, dtype=np.float32)
    for f in feats:
        h = int(hashlib.md5(f.encode()).hexdigest(), 16)
        v[h % DIM] += 1.0 if (h >> 20) & 1 else -1.0
    n = np.linalg.norm(v)
    return v / n if n else v
