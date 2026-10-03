"""Central config. Everything is env-driven so the same code runs locally, in the sandbox and on Nebius."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _p(env: str, default) -> Path:
    return Path(os.environ.get(env, str(default))).expanduser().resolve()


HOME = _p("NOGAIN_HOME", ROOT / "data" / "home")          # the student's data folder
NOTES, CV, JOBS = HOME / "notes", HOME / "cv", HOME / "jobs"
DB_PATH = HOME / "nogain.db"
POLICY_TEMPLATE = _p("NOGAIN_OPENSHELL_POLICY", ROOT / "policy" / "openshell_policy.template.yaml")
APP_POLICY = _p("NOGAIN_APP_POLICY", ROOT / "policy" / "app_policy.yaml")

LLM_MODE = os.environ.get("NOGAIN_LLM", "mock")              # mock | live
BASE_URL = os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
API_KEY = os.environ.get("NEBIUS_API_KEY", "")
MODEL = os.environ.get("NOGAIN_MODEL", "nvidia/nemotron-3-super-120b-a12b")
FAST_MODEL = os.environ.get("NOGAIN_FAST_MODEL", "nvidia/nvidia-nemotron-3-nano-30b-a3b")
BRIEFING_SECONDS = int(os.environ.get("NOGAIN_BRIEFING_SECONDS", "3600"))
