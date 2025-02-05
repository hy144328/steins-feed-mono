import datetime
import enum
import itertools
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

import steins_feed_api.auth
import steins_feed_api.db
import steins_feed_api.pubsub
import steins_feed_api.routers.feeds

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
    summary: typing.Optional[str]
    feed: steins_feed_api.routers.feeds.Feed
    like: typing.Optional[steins_feed_model.items.LikeStatus]
    magic: typing.Optional[float]
    surprise: typing.Optional[float]

    @classmethod
    def from_model(cls, item: steins_feed_model.items.Item) -> "Item":
        return Item(
            id = item.id,
            title = item.title,
            link = item.link,
            summary = item.summary,
            published = item.published.replace(tzinfo=datetime.timezone.utc),
            feed = steins_feed_api.routers.feeds.Feed.from_model(item.feed),
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
    session: steins_feed_api.db.Session,
    current_user: steins_feed_api.auth.UserDep,
    dt_from: datetime.datetime,
    dt_to: datetime.datetime,
    languages: typing.Annotated[
        typing.Optional[typing.Sequence[steins_feed_model.feeds.Language]],
        fastapi.Query(),
    ] = None,
    tags: typing.Annotated[
        typing.Optional[typing.Sequence[int]],
        fastapi.Query(),
    ] = None,
    wall_mode: WallMode = WallMode.CLASSIC,
) -> list[Item]:
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
        steins_feed_model.items.Item.published >= dt_from,
        steins_feed_model.items.Item.published < dt_to,
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
    ).options(
        sqla_orm.contains_eager(
            steins_feed_model.items.Item.feed,
        ).contains_eager(
            steins_feed_model.feeds.Feed.users,
        ),
        sqla_orm.contains_eager(
            steins_feed_model.items.Item.feed,
        ).contains_eager(
            steins_feed_model.feeds.Feed.tags,
        ),
        sqla_orm.joinedload(
            steins_feed_model.items.Item.likes.and_(
                steins_feed_model.items.Like.user_id == current_user.id,
            ),
        ),
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
                for item_it in session.execute(q).scalars().unique()
            ]
        case WallMode.RANDOM:
            rng = random.Random()
            reservoir = steins_feed_magic.sample.Reservoir[Item](rng, 10)

            for item_it in session.execute(q).scalars().unique():
                reservoir.add(Item.from_model(item_it))

            return sorted(reservoir.sample, key=lambda x: x.published, reverse=True)

    q_unscored = q.where(
        steins_feed_model.items.Magic.item_id == None,
    ).order_by(
        steins_feed_model.feeds.Feed.language,
    )
    q_scored = q.where(
        steins_feed_model.items.Magic.item_id != None,
    )

    unscored_items = _augment_unscored(
        items = session.execute(q_unscored).scalars().unique(),
        user_id = current_user.id,
    )

    match wall_mode:
        case WallMode.MAGIC:
            q_scored = q_scored.order_by(
                steins_feed_model.items.Magic.score.desc(),
                steins_feed_model.items.Item.published.desc(),
                steins_feed_model.items.Item.title,
                steins_feed_model.feeds.Feed.title,
            )
            scored_items = (
                Item.from_model(item_it)
                for item_it in session.execute(q_scored).scalars().unique()
            )

            return sorted(
                itertools.chain(scored_items, unscored_items),
                key=lambda x: (
                    -x.magic if x.magic is not None else 0,
                    -x.published.timestamp(),
                    x.title,
                    x.feed.title,
                ),
            )
        case WallMode.SURPRISE:
            scored_items = (
                Item.from_model(item_it)
                for item_it in session.execute(q_scored).scalars().unique()
            )

            rng = random.Random()
            reservoir = steins_feed_magic.sample.Reservoir[Item](rng, 10)

            for item_it in itertools.chain(scored_items, unscored_items):
                reservoir.add(item_it, item_it.surprise or 1)

            return sorted(reservoir.sample, key=lambda x: x.published, reverse=True)

def _augment_unscored(
    items: typing.Iterable[steins_feed_model.items.Item],
    user_id: int,
) -> typing.Generator[Item]:
    res_to_score_by_lang = itertools.groupby(
        items,
        key = lambda x: x.feed.language,
    )
    publishers: list[typing.Generator[Item]] = []

    for k, vs in res_to_score_by_lang:
        if k is None:
            publisher_it = (Item.from_model(v) for v in vs)
            publishers.append(publisher_it)
            continue

        task_it = _calculate_and_update_scores(
            item_ids = [v.id for v in vs],
            user_id = user_id,
            lang = k,
        )
        res_it = task_it.delay()
        assert isinstance(res_it, celery.result.AsyncResult)

        publisher_it = _put_scores(res_it, user_id)
        publishers.append(publisher_it)

    yield from steins_feed_api.pubsub.reduce_publishers(*publishers)

def _calculate_and_update_scores(
    item_ids: typing.Sequence[int],
    user_id: int,
    lang: steins_feed_model.feeds.Language,
) -> celery.canvas.Signature:
    assert isinstance(steins_feed_tasks.magic.calculate_scores, celery.Task)
    assert isinstance(steins_feed_tasks.magic.update_scores, celery.Task)

    calculate_scores = steins_feed_tasks.magic.calculate_scores.s(
        item_ids = item_ids,
        user_id = user_id,
        lang = lang,
    )
    assert isinstance(calculate_scores, celery.canvas.Signature)

    update_scores = steins_feed_tasks.magic.update_scores.s(user_id=user_id)
    assert isinstance(update_scores, celery.canvas.Signature)

    return calculate_scores.set(link=update_scores)

def _put_scores(
    res: celery.result.AsyncResult,
    user_id: int,
) -> typing.Generator[Item]:
    logger.debug(f"Start to process items with scores.")

    item_ids_and_scores = res.get()
    assert item_ids_and_scores is not None

    with sqla_orm.Session(steins_feed_api.db._ENGINE) as session:
        for item_id, item_score in item_ids_and_scores:
            assert isinstance(item_id, int)
            assert isinstance(item_score, typing.Optional[float])

            item_it = session.get_one(
                steins_feed_model.items.Item,
                item_id,
                options = [
                    sqla_orm.joinedload(
                        steins_feed_model.items.Item.feed,
                    ).joinedload(
                        steins_feed_model.feeds.Feed.users.and_(
                            steins_feed_model.users.User.id == user_id,
                        ),
                    ),
                    sqla_orm.joinedload(
                        steins_feed_model.items.Item.feed,
                    ).joinedload(
                        steins_feed_model.feeds.Feed.tags.and_(
                            steins_feed_model.feeds.Tag.user_id == user_id,
                        ),
                    ),
                    sqla_orm.joinedload(
                        steins_feed_model.items.Item.likes.and_(
                            steins_feed_model.items.Like.user_id == user_id,
                        ),
                    ),
                    sqla_orm.noload(steins_feed_model.items.Item.magic),
                ],
            )
            item_it = Item.from_model(item_it)

            if item_score is not None:
                item_it.magic = item_score
                item_it.surprise = Item.magic2surprise(item_score)

            yield item_it

    logger.debug(f"Finish to process items with scores.")

@router.put("/like/")
async def like(
    session: steins_feed_api.db.Session,
    current_user: steins_feed_api.auth.UserDep,
    item_id: int,
    score: steins_feed_model.items.LikeStatus,
):
    q = sqla.select(
        steins_feed_model.items.Like,
    ).where(
        steins_feed_model.items.Like.item_id == item_id,
        steins_feed_model.items.Like.user_id == current_user.id,
    )
    like = session.execute(q).scalar()

    if like is None:
        like = steins_feed_model.items.Like(
            user_id = current_user.id,
            item_id = item_id,
            score = score,
        )
        session.add(like)
    else:
        like.score = score

    session.commit()

@router.get("/analyze_summary")
async def analyze_summary(
    session: steins_feed_api.db.Session,
    current_user: steins_feed_api.auth.UserDep,
    item_id: int,
) -> dict[str, float]:
    item = session.get_one(
        steins_feed_model.items.Item,
        item_id,
        options = [sqla_orm.joinedload(steins_feed_model.items.Item.feed)],
    )

    if item.summary is None:
        return {}

    if item.feed.language is None:
        return {}

    assert isinstance(steins_feed_tasks.magic.analyze_text, celery.Task)
    result = steins_feed_tasks.magic.analyze_text.delay(
        item.summary,
        user_id = current_user.id,
        lang = item.feed.language,
    )

    res = result.get()
    assert isinstance(res, dict)

    return res
