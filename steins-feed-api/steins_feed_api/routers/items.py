import collections.abc
import datetime
import enum
import logging
import random
import typing

import celery
import celery.canvas
import celery.result
import fastapi
import pydantic
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_magic.measure
import steins_feed_magic.sample
import steins_feed_model
import steins_feed_model.feeds
import steins_feed_model.items
import steins_feed_model.users
import steins_feed_tasks.magic

from .. import auth, db
from . import feeds

logger = logging.getLogger(__name__)

router = fastapi.APIRouter(
    prefix = "/items",
    tags = ["items"],
)

class WallMode(enum.Enum):
    CLASSIC = "Classic"
    MAGIC = "Magic"
    RANDOM = "Random"
    SURPRISE = "Surprise"

    @property
    def is_biased(self) -> bool:
        return self in {self.MAGIC, self.SURPRISE}

    @property
    def is_full(self) -> bool:
        return self in {self.CLASSIC, self.MAGIC}

class Item(pydantic.BaseModel):
    id: int
    title: str
    link: str
    published: datetime.datetime
    summary: str | None
    feed: feeds.Feed
    like: steins_feed_model.items.LikeStatus | None
    magic: float | None
    surprise: float | None

    @classmethod
    def from_model(cls, item: steins_feed_model.items.Item) -> "Item":
        return Item(
            id = item.id,
            title = item.title,
            link = item.link,
            summary = item.summary,
            published = item.published.replace(tzinfo=datetime.timezone.utc),
            feed = feeds.Feed.from_model(item.feed),
            like = item.likes[0].score if len(item.likes) > 0 else None,
            magic = item.magic[0].score if len(item.magic) > 0 else None,
            surprise = Item.magic2surprise(item.magic[0].score) if len(item.magic) > 0 else None,
        )

    @staticmethod
    def magic2surprise(score: float) -> float:
        p = (score + 1) / 2
        return steins_feed_magic.measure.entropy_bernoulli(p)

@router.get("/")
async def root(
    session: db.SessionDep,
    current_user: auth.UserDep,
    dt_from: datetime.datetime,
    dt_to: datetime.datetime,
    languages: typing.Annotated[
        collections.abc.Sequence[steins_feed_model.feeds.Language] | None,
        fastapi.Query(),
    ] = None,
    tags: typing.Annotated[
        collections.abc.Sequence[int] | None,
        fastapi.Query(),
    ] = None,
    wall_mode: WallMode = WallMode.CLASSIC,
) -> list[Item]:
    q = _query_root(
        current_user,
        languages = languages,
        tags = tags,
    ).where(
        steins_feed_model.items.Item.published >= dt_from,
        steins_feed_model.items.Item.published < dt_to,
    )

    if wall_mode.is_biased:
        q = q.join(
            steins_feed_model.items.Item.magic.and_(
                steins_feed_model.items.Magic.user_id == current_user.id,
            ),
            isouter = True,
        ).options(
            sqla_orm.contains_eager(steins_feed_model.items.Item.magic),
        )
    else:
        q = q.options(
            sqla_orm.noload(steins_feed_model.items.Item.magic),
        )

    match wall_mode:
        case WallMode.CLASSIC:
            q = q.order_by(
                steins_feed_model.items.Item.published.desc(),
                steins_feed_model.items.Item.title,
                steins_feed_model.feeds.Feed.title,
            )

            return [
                Item.from_model(item_it)
                for item_it in session.scalars(q).unique()
            ]
        case WallMode.RANDOM:
            rng = random.Random()
            reservoir = steins_feed_magic.sample.Reservoir[Item](rng, 10)

            for item_it in session.scalars(q).unique():
                reservoir.add(Item.from_model(item_it))

            return sorted(reservoir.sample, key=lambda x: x.published, reverse=True)

    q_unscored = q.where(
        steins_feed_model.feeds.Feed.language == sqla.bindparam("lang"),
        steins_feed_model.items.Magic.item_id == None,
    ).with_only_columns(
        steins_feed_model.items.Item.id,
    )

    with session.begin():
        tasks = [
            _calculate_and_update_scores(
                item_ids=session.scalars(q_unscored, {"lang": lang_it}).unique().all(),
                user_id=current_user.id,
                lang=lang_it,
            )
            for lang_it in languages or steins_feed_model.feeds.Language
        ]
        job = celery.group(tasks)
        res = job()

    assert isinstance(res, celery.result.GroupResult)
    res.join_native()

    match wall_mode:
        case WallMode.MAGIC:
            q = q.order_by(
                steins_feed_model.items.Magic.score.desc(),
                steins_feed_model.items.Item.published.desc(),
                steins_feed_model.items.Item.title,
                steins_feed_model.feeds.Feed.title,
            )
            return [
                Item.from_model(item_it)
                for item_it in session.scalars(q).unique()
            ]
        case WallMode.SURPRISE:
            rng = random.Random()
            reservoir = steins_feed_magic.sample.Reservoir[Item](rng, 10)

            for item_it in session.scalars(q).unique():
                item_it = Item.from_model(item_it)
                reservoir.add(item_it, item_it.surprise or 1)

            return sorted(reservoir.sample, key=lambda x: x.published, reverse=True)

def _query_root(
    current_user: auth.UserDep,
    languages: collections.abc.Sequence[steins_feed_model.feeds.Language] | None,
    tags: collections.abc.Sequence[int] | None,
    load_display: bool = True,
    load_tags: bool = True,
    load_like: bool = True,
) -> sqla.Select[tuple[steins_feed_model.items.Item]]:
    q = sqla.select(
        steins_feed_model.items.Item,
    ).join(
        steins_feed_model.items.Item.feed,
    ).join(
        steins_feed_model.feeds.Feed.users.and_(
            steins_feed_model.users.User.id == current_user.id,
        ),
    ).join(
        steins_feed_model.feeds.Feed.tags.and_(
            steins_feed_model.feeds.Tag.user_id == current_user.id,
        ),
        isouter = True,
    ).where(
        (
            steins_feed_model.feeds.Feed.language.in_(languages)
            if languages is not None
            else sqla.true()
        ),
        (
            steins_feed_model.feeds.Tag.id.in_(tags)
            if tags is not None
            else sqla.true()
        ),
    )

    if load_display:
        q = q.options(
            sqla_orm.contains_eager(
                steins_feed_model.items.Item.feed,
            ).contains_eager(
                steins_feed_model.feeds.Feed.users,
            ),
        )

    if load_tags:
        q = q.options(
            sqla_orm.contains_eager(
                steins_feed_model.items.Item.feed,
            ).contains_eager(
                steins_feed_model.feeds.Feed.tags,
            ),
        )

    if load_like:
        q = q.options(
            sqla_orm.joinedload(
                steins_feed_model.items.Item.likes.and_(
                    steins_feed_model.items.Like.user_id == current_user.id,
                ),
            ),
        )

    return q

def _calculate_and_update_scores(
    item_ids: collections.abc.Sequence[int],
    user_id: int,
    lang: steins_feed_model.feeds.Language,
) -> celery.canvas.Signature:
    assert isinstance(steins_feed_tasks.magic.calculate_scores, celery.Task)
    calculate_scores = steins_feed_tasks.magic.calculate_scores.s(
        item_ids = item_ids,
        user_id = user_id,
        lang = lang,
    )
    assert isinstance(calculate_scores, celery.canvas.Signature)

    assert isinstance(steins_feed_tasks.magic.update_scores, celery.Task)
    update_scores = steins_feed_tasks.magic.update_scores.s(user_id=user_id)
    assert isinstance(update_scores, celery.canvas.Signature)

    return calculate_scores.set(link=update_scores)

@router.get("/last_updated")
async def last_updated(
    session: db.SessionDep,
    current_user: auth.UserDep,
    languages: typing.Annotated[
        collections.abc.Sequence[steins_feed_model.feeds.Language] | None,
        fastapi.Query(),
    ] = None,
    tags: typing.Annotated[
        collections.abc.Sequence[int] | None,
        fastapi.Query(),
    ] = None,
) -> datetime.datetime:
    q = _query_root(
        current_user,
        languages = languages,
        tags = tags,
        load_display = False,
        load_tags = False,
        load_like = False,
    ).with_only_columns(
        sqla.func.max(steins_feed_model.items.Item.published),
    )
    res = session.scalar(q) or datetime.datetime.fromtimestamp(0)
    res = res.replace(tzinfo = datetime.timezone.utc)

    return res

@router.put("/like/")
async def like(
    session: db.SessionDep,
    current_user: auth.UserDep,
    item_id: int,
    score: steins_feed_model.items.LikeStatus,
):
    q = sqla.select(
        steins_feed_model.items.Like,
    ).where(
        steins_feed_model.items.Like.item_id == item_id,
        steins_feed_model.items.Like.user_id == current_user.id,
    )

    with session.begin():
        like = session.scalar(q)

        if like is None:
            like = steins_feed_model.items.Like(
                user_id = current_user.id,
                item_id = item_id,
                score = score,
            )
            session.add(like)
        else:
            like.score = score

@router.get("/analyze_title")
async def analyze_title(
    session: db.SessionDep,
    current_user: auth.UserDep,
    item_id: int,
) -> list[tuple[str, str, float]]:
    item = session.get_one(
        steins_feed_model.items.Item,
        item_id,
        options = [sqla_orm.joinedload(steins_feed_model.items.Item.feed)],
    )

    if item.feed.language is None:
        return []

    assert isinstance(steins_feed_tasks.magic.analyze_text, celery.Task)
    result = steins_feed_tasks.magic.analyze_text.delay(
        item.title,
        user_id = current_user.id,
        lang = item.feed.language,
    )

    res = result.get()
    assert isinstance(res, list)

    return res

@router.get("/analyze_summary")
async def analyze_summary(
    session: db.SessionDep,
    current_user: auth.UserDep,
    item_id: int,
) -> list[tuple[str, str, float]]:
    item = session.get_one(
        steins_feed_model.items.Item,
        item_id,
        options = [sqla_orm.joinedload(steins_feed_model.items.Item.feed)],
    )

    if item.summary is None:
        return []

    if item.feed.language is None:
        return []

    assert isinstance(steins_feed_tasks.magic.analyze_text, celery.Task)
    result = steins_feed_tasks.magic.analyze_text.delay(
        item.summary,
        user_id = current_user.id,
        lang = item.feed.language,
    )

    res = result.get()
    assert isinstance(res, list)

    return res
