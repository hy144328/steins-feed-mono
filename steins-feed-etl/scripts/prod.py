#!/usr/bin/env python3

import asyncio
import logging.config
import os
import tomllib

import aiohttp
import dotenv
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_etl

dotenv.load_dotenv()

with open(os.path.join(os.path.dirname(__file__), "prod_logging.toml"), "rb") as f:
    logging.config.dictConfig(tomllib.load(f))

async def main():
    url = sqla.URL.create(
        "sqlite",
        username = os.getenv("DB_USER"),
        password = os.getenv("DB_PASS"),
        host = os.getenv("DB_HOST"),
        port = int(os.environ["DB_PORT"]) if "DB_PORT" in os.environ else None,
        database = os.getenv("DB_NAME"),
    )
    engine = sqla.create_engine(url)
    Session = sqla_orm.sessionmaker(engine)

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=5, limit_per_host=1),
    ) as client:
        await steins_feed_etl.parse_feeds(
            Session,
            client,
        )

if __name__ == "__main__":
    asyncio.run(main())
