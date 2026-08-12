import logging

from .app import app

logger = logging.getLogger(__name__)

@app.task
def parse_feeds():
    import asyncio

    logger.info("Start parse_feeds.")
    asyncio.run(parse_feeds_async())
    logger.info("Finish parse_feeds.")

async def parse_feeds_async():
    import aiohttp

    import steins_feed_etl

    from . import db

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=5, limit_per_host=1),
    ) as client:
        await steins_feed_etl.parse_feeds(db.Session, client)
