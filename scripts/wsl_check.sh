#!/usr/bin/env bash
# Hour-0 check for Windows/WSL2 (OpenShell on Windows is "Experimental"; it needs Landlock ABI >= 3 = Linux >= 6.2).
echo "kernel: $(uname -r)  (want >= 6.2)"
echo "LSMs:   $(cat /sys/kernel/security/lsm 2>/dev/null || echo unreadable)  (want 'landlock' in the list)"
docker --version 2>/dev/null || echo "docker: NOT FOUND (Docker Desktop >= 28 with WSL integration)"
command -v openshell >/dev/null && openshell --version || echo "openshell: not installed (see docs.nvidia.com/openshell/about/installation)"
