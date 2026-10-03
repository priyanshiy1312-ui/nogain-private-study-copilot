#!/usr/bin/env bash
# Run from WSL2/Linux with Docker running. Commands below come from the OpenShell docs; flag combinations
# (--from + --policy + `--` command) are NOT verified: run `openshell sandbox create --help` first.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/render_policy.py --home /sandbox/NoGain
rm -rf sandbox/seed && cp -r data/home sandbox/seed && rm -f sandbox/seed/nogain.db
openshell sandbox create --name nogain-demo --policy policy/openshell_policy.yaml --from ./sandbox -- python3 /opt/nogain/sandbox_demo.py
echo "---- OpenShell decision log ----"
openshell logs nogain-demo --since 5m
# Live-edit the policy without restarting (network rules hot-reload):
#   openshell policy get nogain-demo --full > policy/live.yaml  # edit, then:
#   openshell policy set nogain-demo --policy policy/live.yaml --wait
