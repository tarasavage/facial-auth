ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock alembic.ini ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv pip install --system . && \
    uv sync --frozen --no-install-project

COPY ./src /app/src
COPY ./entrypoint.sh /app/entrypoint.sh

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

EXPOSE 8000

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
