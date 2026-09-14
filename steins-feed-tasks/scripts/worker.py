#!/usr/bin/env python3

import logging.config
import sys
import tomllib

import dotenv

dotenv.load_dotenv()

with open("logging.toml", "rb") as f:
    logging.config.dictConfig(tomllib.load(f))

import steins_feed_tasks.celery

steins_feed_tasks.celery.app.worker_main(["worker"] + sys.argv[1:])
