import os

import celery

app = celery.Celery(
    __name__,
    broker = os.environ["BROKER_URL"],
    backend = os.environ["RESULT_BACKEND"],
    include = [
        "steins_feed_tasks.dummy",
        "steins_feed_tasks.etl",
        "steins_feed_tasks.magic",
    ],
)
