import datetime
import typing

import fastapi
import pydantic
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model
import steins_feed_model.feeds
import steins_feed_model.items
import steins_feed_model.users

import steins_feed_api.auth
import steins_feed_api.routers.feeds

router = fastapi.APIRouter(
    prefix = "/items",
    tags = ["items"],
)

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
) -> list[Item]:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.items.Item,
    ).join(
        steins_feed_model.items.Item.feed,
    ).join(
        steins_feed_model.feeds.Feed.users,
    ).where(
        steins_feed_model.users.User.id == current_user.id,
        steins_feed_model.items.Item.published >= dt_from,
        steins_feed_model.items.Item.published < dt_to,
    ).order_by(
        steins_feed_model.items.Item.published.desc(),
    ).options(
        sqla_orm.contains_eager(
            steins_feed_model.items.Item.feed,
        ).joinedload(
            steins_feed_model.feeds.Feed.tags.and_(
                steins_feed_model.feeds.Tag.user_id == current_user.id,
            ),
        ),
        sqla_orm.joinedload(
            steins_feed_model.items.Item.likes.and_(
                steins_feed_model.items.Like.user_id == current_user.id,
            ),
        ),
        sqla_orm.joinedload(
            steins_feed_model.items.Item.magic.and_(
                steins_feed_model.items.Magic.user_id == current_user.id,
            ),
        ),
    )

    with sqla_orm.Session(engine) as session:
        return [
            Item.from_model(item_it)
            for item_it in session.execute(q).scalars().unique()
        ]

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
