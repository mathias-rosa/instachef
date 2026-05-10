FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install dependencies from lockfile only (project code is copied next).
# When building from the repo root, copy pyproject/lock from the api/ subdir.
# If you build with context set to the api/ folder instead, these paths still work
# because Docker resolves the source paths relative to the build context.
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source. Use the api/ subdirectory when the build context is the
# repository root.
COPY api/ .

CMD ["uv", "run", "main.py", "--mode", "telegram", "--forwarded-allow-ips", "*", "--root-path", "/api/v1"]
