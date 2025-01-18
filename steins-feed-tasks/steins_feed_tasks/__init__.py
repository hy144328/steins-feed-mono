#!/usr/bin/env python3

import os

import celery
import dotenv

dotenv.load_dotenv()

app = celery.Celery(
    __name__,
    broker = os.environ["BROKER_URL"],
    backend = os.getenv("RESULT_BACKEND"),
)

@app.task
def add(x, y):
    return x + y
