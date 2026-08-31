#!/usr/bin/env bash
# Pulls the qwen2.5:3b model into the running `ollama` container.
# Not part of docker-compose.yml on purpose — model pulls are a one-time
# convenience step, not something that should block/run on every `up`.
set -euo pipefail

MODEL="${1:-qwen2.5:3b}"
CONTAINER="${OLLAMA_CONTAINER:-$(basename "$(pwd)")-ollama-1}"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  # Fall back to matching any running container from the ollama/ollama image,
  # in case the compose project name produced a different container name.
  CONTAINER="$(docker ps --filter ancestor=ollama/ollama --format '{{.Names}}' | head -n1)"
fi

if [ -z "${CONTAINER}" ]; then
  echo "Could not find a running ollama container. Run 'docker compose up -d ollama' first." >&2
  exit 1
fi

echo "Pulling ${MODEL} into container ${CONTAINER}..."
docker exec "${CONTAINER}" ollama pull "${MODEL}"
