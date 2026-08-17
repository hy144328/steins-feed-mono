FROM python:3.13 AS builder
WORKDIR /usr/src/app

RUN set -o pipefail && curl -sSL https://install.python-poetry.org | python3 - --version 1.8.5
ENV PATH="/root/.local/bin:$PATH"

RUN python3 -m venv --upgrade-deps .venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY steins-feed-model/pyproject.toml steins-feed-model/poetry.lock steins-feed-model/README.md ../steins-feed-model/
COPY steins-feed-model/steins_feed_model ../steins-feed-model/steins_feed_model

COPY steins-feed-config/pyproject.toml steins-feed-config/poetry.lock steins-feed-config/README.md ../steins-feed-config/
COPY steins-feed-config/steins_feed_config ../steins-feed-config/steins_feed_config

COPY steins-feed-etl/pyproject.toml steins-feed-etl/poetry.lock steins-feed-etl/README.md ../steins-feed-etl/
COPY steins-feed-etl/steins_feed_etl ../steins-feed-etl/steins_feed_etl

COPY steins-feed-magic/pyproject.toml steins-feed-magic/poetry.lock steins-feed-magic/README.md ../steins-feed-magic/
COPY steins-feed-magic/steins_feed_magic ../steins-feed-magic/steins_feed_magic

COPY steins-feed-tasks/pyproject.toml steins-feed-tasks/poetry.lock ./
RUN poetry install --with=dev --with=worker --all-extras

FROM python:3.13-slim AS runtime
WORKDIR /usr/src/app

RUN groupadd --gid=1000 app && useradd --uid=1000 --gid=1000 app
USER app

COPY --from=builder /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY steins-feed-model/steins_feed_model ../steins-feed-model/steins_feed_model
COPY steins-feed-config/steins_feed_config ../steins-feed-config/steins_feed_config
COPY steins-feed-etl/steins_feed_etl ../steins-feed-etl/steins_feed_etl
COPY steins-feed-magic/steins_feed_magic ../steins-feed-magic/steins_feed_magic

COPY steins-feed-tasks/steins_feed_tasks ./steins_feed_tasks
ENTRYPOINT ["celery", "-A", "steins_feed_tasks", "worker"]
