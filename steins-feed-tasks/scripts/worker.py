#!/usr/bin/env python3

import sys

import dotenv

dotenv.load_dotenv()

import steins_feed_tasks.celery

print(sys.argv)
steins_feed_tasks.celery.app.worker_main(["worker"] + sys.argv[1:])
