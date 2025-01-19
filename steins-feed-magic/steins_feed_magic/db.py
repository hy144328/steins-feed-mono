import typing

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model.feeds
import steins_feed_model.items

def liked_items(
    session: sqla_orm.Session,
    user_id: int,
    lang: typing.Optional[steins_feed_model.feeds.Language],
    score: steins_feed_model.items.LikeStatus = steins_feed_model.items.LikeStatus.UP,
) -> list[steins_feed_model.items.Item]:
    q = sqla.select(
        steins_feed_model.items.Item,
    ).join(
        steins_feed_model.items.Item.likes,
    ).where(
        steins_feed_model.items.Like.user_id == user_id,
        steins_feed_model.items.Like.score == score,
    )

    if lang is not None:
        q = q.join(
            steins_feed_model.items.Item.feed,
        ).where(
            steins_feed_model.feeds.Feed.language == lang,
        )

    return list(session.execute(q).scalars())

def disliked_items(
    session: sqla_orm.Session,
    user_id: int,
    lang: typing.Optional[steins_feed_model.feeds.Language],
) -> list[steins_feed_model.items.Item]:
    return liked_items(
        session,
        user_id = user_id,
        lang = lang,
        score = steins_feed_model.items.LikeStatus.DOWN,
    )
