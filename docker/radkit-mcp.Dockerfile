FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN pip install uv

COPY radkit-mcp/pyproject.toml radkit-mcp/uv.lock ./
RUN uv sync --locked --no-dev


COPY radkit-mcp/radkit-mcp-profile.py ./mcp-profile.py
COPY radkit-mcp/radkit-mcp-prompt.txt ./prompt.txt
COPY docker/start-radkit-mcp.sh ./docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh && mkdir -p /app/logs

ENTRYPOINT ["/app/docker-entrypoint.sh"]