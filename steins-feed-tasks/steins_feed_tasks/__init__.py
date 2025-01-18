#!/usr/bin/env python3

import celery

app = celery.Celery(
    __name__,
    broker = "redis://localhost:6379/0",
)

@app.task
def add(x, y):
    return x + y
