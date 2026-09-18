#!/usr/bin/env python3

import celery
import celery.result
import dotenv

dotenv.load_dotenv()

import steins_feed_tasks.etl

assert isinstance(steins_feed_tasks.etl.parse_feeds, celery.Task)
res = steins_feed_tasks.etl.parse_feeds.delay()

assert isinstance(res, celery.result.AsyncResult)
res.wait(timeout=300)
