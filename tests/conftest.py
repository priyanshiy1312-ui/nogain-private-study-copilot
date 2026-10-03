import os, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tmp = Path(tempfile.mkdtemp()) / "home"
shutil.copytree(ROOT / "data" / "home", tmp)
os.environ["NOGAIN_HOME"] = str(tmp)      # must be set BEFORE importing app
os.environ["NOGAIN_LLM"] = "mock"
sys.path.insert(0, str(ROOT))
