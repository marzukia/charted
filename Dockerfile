# Container for the charted MCP server (used by Glama and any container host).
# Glama builds this, starts the server over stdio, and checks it answers an
# introspection (tools/list) request.
FROM python:3.12-slim

# cairosvg's PNG export loads libcairo at runtime via cffi.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libcairo2 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir '.[mcp,png]'

# The MCP server speaks stdio.
CMD ["charted-mcp"]
