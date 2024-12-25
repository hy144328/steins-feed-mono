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
    feed: "Feed"
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
            feed = Feed.from_model(item.feed),
            like = item.likes[0].score if len(item.likes) > 0 else None,
            magic = item.magic[0].score if len(item.magic) > 0 else None,
        )

class Feed(pydantic.BaseModel):
    id: int
    title: str
    link: str
    language: typing.Optional[steins_feed_model.feeds.Language]
    tags: list["Tag"]

    @classmethod
    def from_model(cls, feed: steins_feed_model.feeds.Feed) -> "Feed":
        return Feed(
            id = feed.id,
            title = feed.title,
            link = feed.link,
            language = feed.language,
            tags =[Tag.from_model(tag_it) for tag_it in feed.tags],
        )

class Tag(pydantic.BaseModel):
    id: int
    name: str

    @classmethod
    def from_model(cls, tag: steins_feed_model.feeds.Tag) -> "Tag":
        return Tag(
            id = tag.id,
            name = tag.name,
        )

@router.get("/")
async def root(
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
        steins_feed_model.users.User.name == "hansolo",
        steins_feed_model.items.Item.published >= dt_from,
        steins_feed_model.items.Item.published < dt_to,
    ).order_by(
        steins_feed_model.items.Item.published.desc(),
    ).options(
        sqla_orm.contains_eager(
            steins_feed_model.items.Item.feed,
        ).joinedload(
            steins_feed_model.feeds.Feed.tags.and_(
                steins_feed_model.feeds.Tag.user.has(
                    steins_feed_model.users.User.name == "hansolo",
                ),
            ),
        ),
        sqla_orm.joinedload(
            steins_feed_model.items.Item.likes.and_(
                steins_feed_model.items.Like.user.has(
                    steins_feed_model.users.User.name == "hansolo",
                ),
            ),
        ),
        sqla_orm.joinedload(
            steins_feed_model.items.Item.magic.and_(
                steins_feed_model.items.Magic.user.has(
                    steins_feed_model.users.User.name == "hansolo",
                ),
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
    item_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.users.User,
    ).where(
        steins_feed_model.users.User.name == "hansolo",
    )
    with sqla_orm.Session(engine) as session:
        user = session.execute(q).scalars().one()

    q = sqla.select(
        steins_feed_model.items.Like,
    ).where(
        steins_feed_model.items.Like.item_id == item_id,
        steins_feed_model.items.Like.user_id == user.id,
    )

    with sqla_orm.Session(engine) as session:
        like = session.execute(q).scalar()

        if like is None:
            like = steins_feed_model.items.Like(
                user_id = user.id,
                item_id = item_id,
                score = steins_feed_model.items.LikeStatus.UP,
            )
            session.add(like)
        else:
            like.score = (
                steins_feed_model.items.LikeStatus.UP
                if like.score == steins_feed_model.items.LikeStatus.MEH
                else steins_feed_model.items.LikeStatus.MEH
            )

        session.commit()

@router.put("/dislike/")
async def dislike(
    item_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.users.User,
    ).where(
        steins_feed_model.users.User.name == "hansolo",
    )
    with sqla_orm.Session(engine) as session:
        user = session.execute(q).scalars().one()

    q = sqla.select(
        steins_feed_model.items.Like,
    ).where(
        steins_feed_model.items.Like.item_id == item_id,
        steins_feed_model.items.Like.user_id == user.id,
    )

    with sqla_orm.Session(engine) as session:
        like = session.execute(q).scalar()

        if like is None:
            like = steins_feed_model.items.Like(
                user_id = user.id,
                item_id = item_id,
                score = steins_feed_model.items.LikeStatus.DOWN,
            )
            session.add(like)
        else:
            like.score = (
                steins_feed_model.items.LikeStatus.DOWN
                if like.score == steins_feed_model.items.LikeStatus.MEH
                else steins_feed_model.items.LikeStatus.DOWN
            )

        session.commit()
