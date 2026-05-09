FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install dependencies from lockfile only (project code is copied next).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source.
COPY . .

CMD ["uv", "run", "main.py", "--mode", "telegram", "--forwarded-allow-ips", "*", "--root-path", "/api/v1"]