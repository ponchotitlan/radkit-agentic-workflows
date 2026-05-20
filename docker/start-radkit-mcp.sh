#!/bin/sh
set -eu

export FASTMCP_HOST="${RADKIT_MCP_HOST:-0.0.0.0}"

set -- uv run --no-sync radkit-llm mcp-server \
  --port "${RADKIT_MCP_PORT:-8082}" \
  --sandbox "${RADKIT_SANDBOX:-subprocess}" \
  --service-config "${RADKIT_SERVICE_CONFIG:-service.config.direct}" \
  --profile "${RADKIT_PROFILE:-mcp-profile.py}" \
  --prompt "${RADKIT_PROMPT_FILE:-prompt.txt}"

if [ "${RADKIT_AUTO_APPROVE:-true}" = "true" ]; then
  set -- "$@" --auto-approve
fi

if [ -n "${RADKIT_LOGS_HOST_DIR:-}" ]; then
  set -- "$@" --mcp-log-dir "/app/logs"
fi

echo $@

exec "$@"