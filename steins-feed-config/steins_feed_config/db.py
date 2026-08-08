import logging

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model.feeds

logger = logging.getLogger(__name__)

def create_feed(
    session: sqla_orm.Session,
    title: str,
    link: str,
    language: steins_feed_model.feeds.Language | None,
) -> steins_feed_model.feeds.Feed:
    feed = steins_feed_model.feeds.Feed(
        title = title,
        link = link,
        language = language,
    )
    session.add(feed)
    return feed

def get_tag(
    session: sqla_orm.Session,
    user_id: int,
    tag_name: str,
) -> steins_feed_model.feeds.Tag:
    q = sqla.select(
        steins_feed_model.feeds.Tag,
    ).where(
        steins_feed_model.feeds.Tag.user_id == user_id,
        steins_feed_model.feeds.Tag.name == tag_name,
    )
    return session.execute(q).scalars().one()

def create_tag(
    session: sqla_orm.Session,
    user_id: int,
    tag_name: str,
) -> steins_feed_model.feeds.Tag:
    tag = steins_feed_model.feeds.Tag(
        user_id = user_id,
        name = tag_name,
    )
    session.add(tag)
    return tag

def get_feeds(session: sqla_orm.Session) -> list[steins_feed_model.feeds.Feed]:
    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).order_by(
        sqla.collate(steins_feed_model.feeds.Feed.title, "NOCASE"),
    )
    return list(session.execute(q).scalars().unique())
