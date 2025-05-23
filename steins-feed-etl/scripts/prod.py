#!/usr/bin/env python3

import asyncio
import logging.config
import os
import tomllib

import aiohttp
import dotenv
import sqlalchemy.orm as sqla_orm

import steins_feed_etl
import steins_feed_model

dotenv.load_dotenv()

with open(os.path.join(os.path.dirname(__file__), "prod_logging.toml"), "rb") as f:
    logging.config.dictConfig(tomllib.load(f))

async def main():
    engine = steins_feed_model.EngineFactory.create_engine(
        username = os.getenv("DB_USER"),
        password = os.getenv("DB_PASS"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        database = os.getenv("DB_NAME"),
    )
    connector = aiohttp.TCPConnector(limit=5, limit_per_host=1)

    with sqla_orm.Session(engine) as session:
        async with aiohttp.ClientSession(connector=connector) as client:
            await steins_feed_etl.parse_feeds(
                session,
                client,
                skip_recent = True,
            )

if __name__ == "__main__":
    asyncio.run(main())
