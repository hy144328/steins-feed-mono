import asyncio
import datetime
import typing

import aiohttp
import feedparser
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import tenacity

import steins_feed_logging
import steins_feed_model.feeds
import steins_feed_model.items

from . import util

# Logger.
logger = steins_feed_logging.LoggerFactory.get_logger(__name__)

async def parse_feeds(
    session: sqla_orm.Session,
    title_pattern=None,
):
    q_feeds = asyncio.Queue()
    q_items = asyncio.Queue()

    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).order_by(
        sqla.collate(steins_feed_model.feeds.Feed.title, "NOCASE"),
    )
    if title_pattern:
        q = q.where(steins_feed_model.feeds.Feed.title.like(f"%{title_pattern}%"))

    for feed_it in session.execute(q).scalars():
        await q_feeds.put(feed_it)

    logger.info(f"{q_feeds.qsize()} feeds.")

    async with asyncio.TaskGroup() as tg:
        tg.create_task(write_items(session, q_items))
        logger.info("Writer started.")

        async with aiohttp.ClientSession() as web_session:
            while not q_feeds.empty():
                feed_it = await q_feeds.get()
                future_it = read_feed(
                    web_session,
                    q_items,
                    feed = feed_it,
                    task_done = q_feeds.task_done,
                )
                tg.create_task(future_it)

            logger.info("Readers started.")
            await q_feeds.join()
            logger.info("Readers finished.")

        await q_items.put(None)

    logger.info("Writer finished.")

async def write_items(
    session: sqla_orm.Session,
    q_items: asyncio.Queue,
    batch_size: int = 200,
):
    q = sqla.insert(steins_feed_model.items.Item)
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    no_items_total = 0

    async for item_batch_it in util.batch_queue(q_items, batch_size):
        no_items = len(item_batch_it)
        logger.debug(f"From {no_items_total + 1} to {no_items_total + no_items}.")
        no_items_total += no_items

        res_batch_it = []

        for item_it in item_batch_it:
            assert isinstance(item_it, steins_feed_model.items.Item)

            res_it = {
                "title": item_it.title,
                "link": item_it.link,
                "published": item_it.published,
                "feed_id": item_it.feed_id,
                "summary": item_it.summary,
            }

            res_batch_it.append(res_it)

        session.execute(q, res_batch_it)

    session.commit()

@tenacity.retry(
    retry=tenacity.retry_if_exception_type(aiohttp.ClientResponseError),
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(),
)
async def read_feed(
    session: aiohttp.ClientSession,
    q_items: asyncio.Queue,
    feed: steins_feed_model.feeds.Feed,
    task_done: typing.Callable[[], None],
):
    async with session.get(feed.link) as resp:
        status = resp.status

        if status < 300:
            logger.info(f"{feed.title} -- {status}.")
        elif status < 400:
            logger.warning(f"{feed.title} -- {status}.")
        elif status == 429:     # too many requests
            logger.warning(f"{feed.title} -- {status}.")
            resp.raise_for_status()
        else:
            logger.error(f"{feed.title} -- {status}.")
            resp.raise_for_status()

        text = await resp.text()

    res = feedparser.parse(text)
    logger.info(f"{len(res.entries)} items from {feed.title} total.")

    for entry_it in res.entries:
        try:
            item_it = read_item(entry_it, feed)
            await q_items.put(item_it)
        except AttributeError:
            logger.error(f"Skip item from {feed.title}:\n{entry_it}")

    logger.info(f"{len(res.entries)} valid items from {feed.title}.")
    task_done()

def read_item(
    entry,
    feed: steins_feed_model.feeds.Feed,
) -> steins_feed_model.items.Item:
    return steins_feed_model.items.Item(
        title = read_item_title(entry),
        link = read_item_link(entry),
        published = read_item_time(entry),
        feed_id = feed.id,
        summary = read_item_summary(entry),
    )

def read_item_title(item) -> str:
    try:
        item_title = item.title
        return item_title
    except AttributeError:
        pass

    logger.error("No title.")
    raise AttributeError

def read_item_link(item) -> str:
    try:
        item_link = item.link
        return item_link
    except AttributeError:
        pass

    try:
        item_link = item.links[0].href
        return item_link
    except AttributeError:
        pass

    logger.error(f"No link for '{read_item_title(item)}'.")
    raise AttributeError

def read_item_summary(item) -> str:
    return item.summary

def read_item_time(item) -> datetime.datetime:
    try:
        item_time = item.published_parsed
        item_time = datetime.datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    try:
        item_time = item.updated_parsed
        item_time = datetime.datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    logger.error(f"No time for '{read_item_title(item)}'.")
    raise AttributeError
