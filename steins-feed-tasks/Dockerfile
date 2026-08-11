FROM python:3.13 AS builder
WORKDIR /usr/src/app

RUN set -o pipefail && curl -sSL https://install.python-poetry.org | python3 - --version 1.8.5
ENV PATH="/root/.local/bin:$PATH"

RUN python3 -m venv --upgrade-deps .venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN poetry install

FROM python:3.13-slim AS runtime
WORKDIR /usr/src/app

RUN groupadd --gid=1000 app && useradd --uid=1000 --gid=1000 app
USER app

COPY --from=builder /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY steins_feed_tasks ./steins_feed_tasks
ENTRYPOINT ["celery", "-A", "steins_feed_tasks", "worker"]
