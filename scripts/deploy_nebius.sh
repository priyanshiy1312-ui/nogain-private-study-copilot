#!/usr/bin/env bash
# Deploy the API as a Nebius Serverless AI endpoint. Flags taken from docs.nebius.com/serverless (public preview).
# Needs: nebius CLI (install + `nebius profile create` in an interactive shell), an image in a registry.
set -euo pipefail
IMAGE="${1:?usage: deploy_nebius.sh <registry/image:tag>}"
TOKEN="${ENDPOINT_TOKEN:-$(openssl rand -hex 32)}"
nebius ai endpoint create --name nogain-api --image "$IMAGE" \
  --platform cpu-d3 --preset 4vcpu-16gb --public --container-port 8000 \
  --auth token --token "$TOKEN" \
  --env "NOGAIN_LLM=live" --env "NEBIUS_API_KEY=${NEBIUS_API_KEY:?set NEBIUS_API_KEY}" \
  --env "NOGAIN_BRIEFING_SECONDS=30"
ID=$(nebius ai endpoint get-by-name --name nogain-api --format jsonpath='{.metadata.id}')
echo "endpoint id: $ID  token: $TOKEN"
nebius ai endpoint get "$ID" --format jsonpath='{.status.public_endpoints[0]}'
