# Ask ABUZ8 — MCP server (spec 2025-11-25, Streamable HTTP) + simulator.
#
#   docker build -t ask-abuz8 .
#   docker run -d --name ask-abuz8 -p 127.0.0.1:8377:8377 \
#       -v ask-abuz8-data:/app/data ask-abuz8
#
# Publish only to the host's loopback and put a TLS reverse proxy in front
# (see HOSTING.md). The port inside the container is $PORT (default 8377).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8377 \
    FASTMCP_HOST=0.0.0.0

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server/ ./mcp_server/
COPY data/ ./data/
COPY simulator/ ./simulator/

# FASTMCP_HOST: the MCP Python SDK reads FASTMCP_-prefixed env vars, so the
# server binds 0.0.0.0 *inside the container* with zero code changes.
# Decisions append to data/feed.runtime.json (seeded from data/feed.json on
# first run) — mount a volume at /app/data to persist the ledger.
EXPOSE 8377

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8377/health', timeout=4).status == 200 else 1)"

CMD ["python", "mcp_server/server.py"]
