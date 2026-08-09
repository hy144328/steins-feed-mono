import asyncio
import logging
import typing

import aiohttp
import dateutil.parser
import feedparser
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import tenacity

import steins_feed_model.feeds
import steins_feed_model.items

from . import parse, util

logger = logging.getLogger(__name__)

BATCH_SIZE = 200

async def parse_feeds(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client: aiohttp.ClientSession,
    title_pattern: str | None = None,
):
    q_feeds: asyncio.Queue[steins_feed_model.feeds.Feed] = asyncio.Queue()
    q_items: asyncio.Queue[steins_feed_model.items.Item] = asyncio.Queue()

    with Session() as writer_session:
        asyncio.create_task(write_items(writer_session, q_items))
        logger.info("Writer started.")

        with Session(expire_on_commit=False) as loader_session:
            asyncio.create_task(load_feeds(loader_session, q_feeds, title_pattern))
            logger.info("Loader started.")

            while True:
                try:
                    feed_it = await q_feeds.get()
                except asyncio.QueueShutDown:
                    logger.info("Loader finished.")
                    break

                future_it = read_feed(
                    client,
                    q_items,
                    feed = feed_it,
                    task_done = q_feeds.task_done,
                )
                asyncio.create_task(future_it)
                logger.info("Reader started.")

        await q_feeds.join()
        logger.info("Readers finished.")

        q_items.shutdown()
        await q_items.join()
        logger.info("Writer finished.")

async def load_feeds(
    session: sqla_orm.Session,
    queue: asyncio.Queue[steins_feed_model.feeds.Feed],
    title_pattern: str | None = None,
):
    q = sqla.select(steins_feed_model.feeds.Feed)
    if title_pattern:
        q = q.where(steins_feed_model.feeds.Feed.title.like(f"%{title_pattern}%"))

    with session.begin():
        for feed_it in session.scalars(q):
            await queue.put(feed_it)

    queue.shutdown()

async def write_items(
    session: sqla_orm.Session,
    queue: asyncio.Queue[steins_feed_model.items.Item],
    batch_size: int = BATCH_SIZE,
):
    stmt = sqla.insert(steins_feed_model.items.Item)
    stmt = stmt.prefix_with("OR IGNORE", dialect="sqlite")
    no_items_total = 0

    async for item_batch_it in util.batch_queue(queue, batch_size):
        no_items = len(item_batch_it)
        logger.debug(f"From {no_items_total + 1} to {no_items_total + no_items}.")
        no_items_total += no_items

        res_batch_it = [
            {
                "title": item_it.title,
                "link": item_it.link,
                "published": item_it.published,
                "feed_id": item_it.feed_id,
                "summary": item_it.summary,
            }
            for item_it in item_batch_it
        ]
        with session.begin():
            session.execute(stmt, res_batch_it)

        for _ in range(no_items):
            queue.task_done()

async def read_feed(
    client: aiohttp.ClientSession,
    queue: asyncio.Queue[steins_feed_model.items.Item],
    feed: steins_feed_model.feeds.Feed,
    task_done: typing.Callable[[], None],
):
    try:
        async for attempt_it in tenacity.AsyncRetrying(
            retry=tenacity.retry_if_exception_type(aiohttp.ClientError),
            stop=tenacity.stop_after_attempt(3),
            wait=tenacity.wait_exponential(),
        ):
            with attempt_it:
                try:
                    async with client.get(feed.link) as resp:
                        status = resp.status

                        if status < 300:
                            logger.info(f"{feed.title} -- {status}.")
                        elif status < 400:  # pragma: no cover
                            logger.warning(f"{feed.title} -- {status}.")
                        elif status == 429:     # pragma: no cover
                            logger.warning(f"{feed.title} -- {status}.")
                            resp.raise_for_status()
                        else:   # pragma: no cover
                            logger.error(f"{feed.title} -- {status}.")
                            resp.raise_for_status()

                        text = await resp.text()

                    res = feedparser.parse(text)
                    logger.info(f"{len(res.entries)} items from {feed.title} total.")
                    no_valid = 0

                    for entry_it in res.entries:
                        assert isinstance(entry_it, feedparser.FeedParserDict)

                        try:
                            item_it = parse.read_item(entry_it, feed.id)
                            await queue.put(item_it)
                            no_valid += 1
                        except AttributeError:  # pragma: no cover
                            logger.error(f"Skip item from {feed.title}:\n{entry_it}")
                        except dateutil.parser.ParserError: # pragma: no cover
                            logger.error(f"Skip item from {feed.title}:\n{entry_it}")

                    logger.info(f"{no_valid} valid items from {feed.title}.")
                except aiohttp.ClientResponseError as e:    # pragma: no cover
                    logger.error(f"No items from {feed.title}.\n{e}")
                except aiohttp.ConnectionTimeoutError as e: # pragma: no cover
                    logger.warning(f"Too slow for {feed.title}.\n{e}")
                    raise e
                except aiohttp.ClientConnectorCertificateError as e:    # pragma: no cover
                    logger.error(f"Bad certificate for {feed.title}.\n{e}")
                except aiohttp.ClientConnectorError as e:   # pragma: no cover
                    logger.warning(f"Bad luck for {feed.title}.\n{e}")
                    raise e
    except tenacity.RetryError: # pragma: no cover
        pass
    finally:
        task_done()
