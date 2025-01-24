import collections
import datetime
import enum
import functools
import random
import typing

import celery
import celery.canvas
import celery.result
import fastapi
import numpy as np
import pydantic
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_logging
import steins_feed_model
import steins_feed_model.feeds
import steins_feed_model.items
import steins_feed_model.users
import steins_feed_tasks.magic

import steins_feed_api.auth
import steins_feed_api.routers.feeds

router = fastapi.APIRouter(
    prefix = "/items",
    tags = ["items"],
)

logger = steins_feed_logging.LoggerFactory.get_logger(__name__)

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
        )

@router.get("/")
async def root(
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
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

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

    match wall_mode:
        case WallMode.MAGIC:
            q = q.order_by(
                steins_feed_model.items.Magic.score.desc(),
                steins_feed_model.items.Item.published.desc(),
                steins_feed_model.items.Item.title,
                steins_feed_model.feeds.Feed.title,
            )
        case _:
            q = q.order_by(
                steins_feed_model.items.Item.published.desc(),
                steins_feed_model.items.Item.title,
                steins_feed_model.feeds.Feed.title,
            )

    if wall_mode.is_biased:
        q = q.options(
            sqla_orm.joinedload(
                steins_feed_model.items.Item.magic.and_(
                    steins_feed_model.items.Magic.user_id == current_user.id,
                ),
            ),
        )
    else:
        q = q.options(sqla_orm.noload(steins_feed_model.items.Item.magic))

    match wall_mode:
        case WallMode.CLASSIC:
            with sqla_orm.Session(engine) as session:
                return [
                    Item.from_model(item_it)
                    for item_it in session.execute(q).scalars().unique()
                ]
        case WallMode.RANDOM:
            with sqla_orm.Session(engine) as session:
                res = [
                    Item.from_model(item_it)
                    for item_it in session.execute(q).scalars().unique()
                ]
                return random.sample(res, 10)

    res: list[Item] = []
    res_to_score_by_lang: dict[steins_feed_model.feeds.Language, list[Item]] = collections.defaultdict(list)

    with sqla_orm.Session(engine) as session:
        for item_it in session.execute(q).scalars().unique():
            res_it = Item.from_model(item_it)
            res.append(res_it)

            if (res_it.magic is None) and (res_it.feed.language is not None):
                res_to_score_by_lang[res_it.feed.language].append(res_it)

    job_tasks = []

    for k, vs in res_to_score_by_lang.items():
        job_task_it = _calculate_and_update_scores(
            user_id = current_user.id,
            lang = k,
            item_ids = [v.id for v in vs],
        )
        job_tasks.append(job_task_it)

    job = celery.group(*job_tasks)
    g = job()
    assert isinstance(g, celery.result.GroupResult)

    for result_it, vs in zip(g.results, res_to_score_by_lang.values()):
        assert isinstance(result_it, celery.result.AsyncResult)
        result_it.then(functools.partial(_set_scores, items=vs))

    g.forget()

    match wall_mode:
        case WallMode.MAGIC:
            return res
        case WallMode.SURPRISE:
            scores = np.array(res_it.magic or 0 for res_it in res)
            return random.choices(res, k=10, weights=np.log((1 + scores) / (1 - scores)))

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

    update_scores = steins_feed_tasks.magic.update_scores.s(
        user_id = user_id,
        lang = lang,
    )
    assert isinstance(update_scores, celery.canvas.Signature)

    return calculate_scores.set(link=update_scores)

def _set_scores(
    res: celery.result.AsyncResult,
    items: typing.Sequence[Item],
):
    logger.info(f"Start to augment {len(items)} items with scores.")

    id2score = dict(res.result)

    for item_it in items:
        item_it.magic = id2score[item_it.id]

    logger.info(f"Finish to augment {len(items)} items with scores.")

@router.put("/like/")
async def like(
    current_user: steins_feed_api.auth.UserDep,
    item_id: int,
    score: steins_feed_model.items.LikeStatus,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.items.Like,
    ).where(
        steins_feed_model.items.Like.item_id == item_id,
        steins_feed_model.items.Like.user_id == current_user.id,
    )

    with sqla_orm.Session(engine) as session:
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
