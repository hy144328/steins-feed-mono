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
    import sqlalchemy.orm as sqla_orm

    import steins_feed_etl

    from . import db

    connector = aiohttp.TCPConnector(limit=5, limit_per_host=1)

    with sqla_orm.Session(db.engine) as session:
        async with aiohttp.ClientSession(connector=connector) as client:
            await steins_feed_etl.parse_feeds(session, client, skip_recent=True)
