#!/usr/bin/env python3

import asyncio
import logging
import os

import aiohttp
import celery
import dotenv
import sqlalchemy.orm as sqla_orm

import steins_feed_etl.items
import steins_feed_logging
import steins_feed_model

dotenv.load_dotenv()

app = celery.Celery(
    __name__,
    broker = os.environ["BROKER_URL"],
    backend = os.getenv("RESULT_BACKEND"),
)

try:
    os.mkdir("logs.d")
except FileExistsError:
    pass

with open("logs.d/steins_feed_etl.log", "a") as f:
    etl_logger = steins_feed_logging.LoggerFactory.get_logger(steins_feed_etl.items.__name__)
    steins_feed_logging.LoggerFactory.add_file_handler(etl_logger, f)
    steins_feed_logging.LoggerFactory.set_level(etl_logger, level=logging.INFO)

@app.task
def add(x, y):
    return x + y

@app.task
def parse_feeds():
    asyncio.run(parse_feeds_async())

async def parse_feeds_async():
    engine = steins_feed_model.EngineFactory.get_or_create_engine(database=os.environ["DB_NAME"])
    connector = aiohttp.TCPConnector(limit=5, limit_per_host=1)

    with sqla_orm.Session(engine) as session:
        async with aiohttp.ClientSession(connector=connector) as client:
            await steins_feed_etl.items.parse_feeds(session, client, skip_recent=True)
