import os

import celery

app = celery.Celery(
    __name__,
    broker = os.environ["BROKER_URL"],
    backend = os.getenv("RESULT_BACKEND"),
    include = [
        "steins_feed_tasks.dummy",
        "steins_feed_tasks.etl",
    ],
)
