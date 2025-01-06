import asyncio
import datetime
import random
import typing

import aiohttp
import dateutil.parser
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
    client: aiohttp.ClientSession,
    title_pattern: typing.Optional[str] = None,
    skip_recent: bool = False,
):
    now = datetime.datetime.now(datetime.timezone.utc)

    q_feeds = asyncio.Queue()
    q_items = asyncio.Queue()

    q = sqla.select(steins_feed_model.feeds.Feed)
    if title_pattern:
        q = q.where(steins_feed_model.feeds.Feed.title.like(f"%{title_pattern}%"))

    feeds = session.execute(q).scalars().all()
    feeds = random.sample(feeds, k=len(feeds))

    for feed_it in feeds:
        if skip_recent:
            q_stat = sqla.select(
                sqla.func.count(),
                sqla.func.min(steins_feed_model.items.Item.published),
                sqla.func.max(steins_feed_model.items.Item.published),
            ).where(
                steins_feed_model.items.Item.feed_id == feed_it.id,
                steins_feed_model.items.Item.published > now - datetime.timedelta(days=30)
            )
            res_stat = session.execute(q_stat).tuples().one_or_none()

            if res_stat is not None and res_stat[0] > 1:
                dt_last = res_stat[2].replace(tzinfo=datetime.timezone.utc)
                td_mean = (res_stat[2] - res_stat[1]) / (res_stat[0] - 1)
                dt_next = dt_last + td_mean

                if now < dt_next:
                    logger.warning(f"Skip {feed_it.title} until {dt_next}.")
                    continue
                else:
                    logger.debug(f"{feed_it.title} due since {dt_next}.")

        await q_feeds.put(feed_it)

    logger.info(f"{q_feeds.qsize()} feeds.")

    async with asyncio.TaskGroup() as tg:
        tg.create_task(write_items(session, q_items))
        logger.info("Writer started.")

        while not q_feeds.empty():
            feed_it = await q_feeds.get()
            future_it = read_feed(
                client,
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
    client: aiohttp.ClientSession,
    q_items: asyncio.Queue,
    feed: steins_feed_model.feeds.Feed,
    task_done: typing.Callable[[], None],
):
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

    for entry_it in res.entries:
        try:
            item_it = read_item(entry_it, feed)
            await q_items.put(item_it)
        except AttributeError:  # pragma: no cover
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
        published = read_item_time(entry).astimezone(datetime.timezone.utc),
        feed_id = feed.id,
        summary = read_item_summary(entry),
    )

def read_item_title(item) -> str:
    try:
        item_title = item.title
        return item_title
    except AttributeError:  # pragma: no cover
        pass

    logger.error("No title.")   # pragma: no cover
    raise AttributeError    # pragma: no cover

def read_item_link(item) -> str:
    try:
        item_link = item.link
        return item_link
    except AttributeError:  # pragma: no cover
        pass

    try:
        item_link = item.links[0].href
        return item_link
    except AttributeError:  # pragma: no cover
        pass

    logger.error(f"No link for '{read_item_title(item)}'.") # pragma: no cover
    raise AttributeError    # pragma: no cover

def read_item_summary(item) -> str:
    return item.summary

def read_item_time(item) -> datetime.datetime:
    try:
        item_time = item.published
        item_time = dateutil.parser.parse(item_time)
        return item_time
    except (AttributeError, TypeError): # pragma: no cover
        pass

    try:
        item_time = item.updated
        item_time = dateutil.parser.parse(item_time)
        return item_time
    except (AttributeError, TypeError): # pragma: no cover
        pass

    logger.error(f"No time for '{read_item_title(item)}'.") # pragma: no cover
    raise AttributeError    # pragma: no cover
