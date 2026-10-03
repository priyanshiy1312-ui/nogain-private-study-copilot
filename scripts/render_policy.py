#!/usr/bin/env python3
"""Render policy/openshell_policy.template.yaml -> policy/openshell_policy.yaml with absolute paths.
usage: python scripts/render_policy.py --home /sandbox/NoGain"""
import argparse
from pathlib import Path

root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--home", default="/sandbox/NoGain", help="NoGain data dir AS SEEN INSIDE the sandbox")
a = ap.parse_args()
src = (root / "policy" / "openshell_policy.template.yaml").read_text().replace("__NOGAIN_HOME__", a.home)
(root / "policy" / "openshell_policy.yaml").write_text(src)
print(f"wrote policy/openshell_policy.yaml (home={a.home})")
