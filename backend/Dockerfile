ARG PYTHON_VERSION=3.13 AS BUILDER

## ------------------------------- Builder Stage ------------------------------ ## 
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.6.7 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv pip install --system . && \
    uv sync --frozen --no-install-project


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync


## ------------------------------- Production Stage ------------------------------ ## 

FROM --platform=linux/amd64 python:3.13-slim-bookworm AS production


WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY ./src src
COPY ./alembic.ini alembic.ini
COPY ./entrypoint.sh entrypoint.sh


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

EXPOSE 8000

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
