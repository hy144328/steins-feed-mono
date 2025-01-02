#!/usr/bin/env python3

import asyncio
import logging
import os

import aiohttp
import dotenv
import sqlalchemy.orm as sqla_orm

import steins_feed_etl.items
import steins_feed_logging
import steins_feed_model

dotenv.load_dotenv()

logger = steins_feed_logging.LoggerFactory.get_logger(steins_feed_etl.items.__name__)
steins_feed_logging.LoggerFactory.add_file_handler(logger)
steins_feed_logging.LoggerFactory.set_level(logger, level=logging.INFO)

async def main():
    engine = steins_feed_model.EngineFactory.get_or_create_engine(database=os.environ["DB_NAME"])

    with sqla_orm.Session(engine) as session:
        async with aiohttp.ClientSession() as client:
            await steins_feed_etl.items.parse_feeds(session, client, skip_recent=True)

if __name__ == "__main__":
    asyncio.run(main())
