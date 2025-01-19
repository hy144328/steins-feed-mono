import logging
import os

import steins_feed_logging

from .app import app

try:
    os.mkdir("logs.d")
except FileExistsError:
    pass

with open("logs.d/steins_feed_etl.log", "a") as f:
    etl_logger = steins_feed_logging.LoggerFactory.get_logger("steins_feed_etl.items")
    steins_feed_logging.LoggerFactory.add_file_handler(etl_logger, f)
    steins_feed_logging.LoggerFactory.set_level(etl_logger, level=logging.INFO)

@app.task
def parse_feeds():
    import asyncio

    asyncio.run(parse_feeds_async())

async def parse_feeds_async():
    import aiohttp
    import sqlalchemy.orm as sqla_orm

    import steins_feed_etl.items

    from .db import engine

    connector = aiohttp.TCPConnector(limit=5, limit_per_host=1)

    with sqla_orm.Session(engine) as session:
        async with aiohttp.ClientSession(connector=connector) as client:
            await steins_feed_etl.items.parse_feeds(session, client, skip_recent=True)
