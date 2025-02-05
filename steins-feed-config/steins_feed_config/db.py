import logging
import typing

import sqlalchemy as sqla
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm

import steins_feed_model.feeds
import steins_feed_model.users

logger = logging.getLogger(__name__)

def get_or_create_feed(
    session: sqla_orm.Session,
    title: str,
    link: str,
    language: typing.Optional[steins_feed_model.feeds.Language],
) -> steins_feed_model.feeds.Feed:
    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).where(
        steins_feed_model.feeds.Feed.title == title,
    )

    try:
        feed = session.execute(q).scalars().one()

        logger.info(f"Get {title}.")
    except sqla_exc.NoResultFound:
        feed = steins_feed_model.feeds.Feed(
            title = title,
            link = link,
            language = language,
        )
        session.add(feed)
        session.commit()

        logger.warning(f"Create {title}.")

    return feed

def get_or_create_tag(
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

    try:
        tag = session.execute(q).scalars().one()

        logger.info(f"Get {tag_name}.")
    except sqla_exc.NoResultFound:
        tag = steins_feed_model.feeds.Tag(
            user_id = user_id,
            name = tag_name,
        )
        session.add(tag)
        session.commit()

        logger.warning(f"Create {tag_name}.")

    return tag

def add_tag(
    session: sqla_orm.Session,
    feed: steins_feed_model.feeds.Feed,
    tag: steins_feed_model.feeds.Tag,
):
    feed_title = feed.title
    tag_name = tag.name

    try:
        feed.tags.append(tag)
        session.commit()
        logger.info(f"Add {tag_name} to {feed_title}.")
    except sqla_exc.IntegrityError:
        logger.warning(f"{feed_title} already in {tag_name}.")
        session.rollback()

def get_feeds(session: sqla_orm.Session) -> list[steins_feed_model.feeds.Feed]:
    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).order_by(
        sqla.collate(steins_feed_model.feeds.Feed.title, "NOCASE"),
    )
    return list(session.execute(q).scalars().unique())
