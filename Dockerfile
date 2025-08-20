ARG ENVIRONMENT=DEVELOPMENT

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=0 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    if [ "${ENVIRONMENT}" = "PRODUCTION" ]; then \
    uv sync --frozen --no-install-project --no-dev; \
    else \
    uv sync --frozen --no-install-project --all-groups; \
    fi

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    if [ "${ENVIRONMENT}" = "PRODUCTION" ]; then \
    uv sync --frozen --no-dev; \
    else \
    uv sync --frozen --all-groups; \
    fi


FROM python:3.13-slim-bookworm AS final

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app /app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

CMD [ "granian", "--interface", "asgi", "--workers", "4", "--factory", "yt_dlp_api.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info" ]