import datetime
import logging

import dateutil.parser
import feedparser

import steins_feed_model.items

logger = logging.getLogger(__name__)

def read_item(
    entry: feedparser.FeedParserDict,
    feed_id: int,
) -> steins_feed_model.items.Item:
    return steins_feed_model.items.Item(
        title = read_item_title(entry),
        link = read_item_link(entry),
        published = read_item_time(entry).astimezone(datetime.timezone.utc),
        feed_id = feed_id,
        summary = read_item_summary(entry),
    )

def read_item_title(entry: feedparser.FeedParserDict) -> str:
    excs: list[Exception] = []

    try:
        return entry.title
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no title field.")
        excs.append(e)

    raise ExceptionGroup("No title.", excs) # pragma: no cover

def read_item_link(entry: feedparser.FeedParserDict) -> str:
    excs: list[Exception] = []

    try:
        return entry.link
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no link field.")
        excs.append(e)

    try:    # pragma: no cover
        return entry.links[0].href
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no links field.")
        excs.append(e)

    raise ExceptionGroup("No link.", excs) # pragma: no cover

def read_item_summary(entry: feedparser.FeedParserDict) -> str | None:
    try:
        return entry.summary
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no summary field.")

    return None # pragma: no cover

def read_item_time(entry: feedparser.FeedParserDict) -> datetime.datetime:
    excs: list[Exception] = []

    try:
        return dateutil.parser.parse(entry.published)
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no published field.")
        excs.append(e)
    except dateutil.parser.ParserError as e:    # pragma: no cover
        logger.warning(f"Unable to parse published field: {entry.published}.")
        excs.append(e)

    try:    # pragma: no cover
        return dateutil.parser.parse(entry.updated)
    except AttributeError as e: # pragma: no cover
        logger.warning("Item has no updated field.")
        excs.append(e)
    except dateutil.parser.ParserError as e:    # pragma: no cover
        logger.warning(f"Unable to parse updated field: {entry.updated}.")
        excs.append(e)

    raise ExceptionGroup("No time.", excs)  # pragma: no cover
