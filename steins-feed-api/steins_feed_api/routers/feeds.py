import typing

import fastapi
import pydantic
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_logging
import steins_feed_model
import steins_feed_model.feeds
import steins_feed_model.users

import steins_feed_api.auth

router = fastapi.APIRouter(
    prefix = "/feeds",
    tags = ["feeds"],
)
logger = steins_feed_logging.LoggerFactory.get_logger(__name__)

class Feed(pydantic.BaseModel):
    id: int
    title: str
    link: str
    language: typing.Optional[steins_feed_model.feeds.Language]
    tags: list["Tag"]
    displayed: typing.Optional[bool]

    @classmethod
    def from_model(cls, feed: steins_feed_model.feeds.Feed) -> "Feed":
        return Feed(
            id = feed.id,
            title = feed.title,
            link = feed.link,
            language = feed.language,
            tags = [Tag.from_model(tag_it) for tag_it in feed.tags],
            displayed = (len(feed.users) > 0),
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

@router.get("/tags/")
async def tags(
    current_user: steins_feed_api.auth.UserDep,
) -> list[Tag]:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.feeds.Tag,
    ).where(
        steins_feed_model.feeds.Tag.user_id == current_user.id,
    ).order_by(
        steins_feed_model.feeds.Tag.name,
    )

    with sqla_orm.Session(engine) as session:
        return [
            Tag.from_model(tag_it)
            for tag_it in session.execute(q).scalars()
        ]

@router.get("/languages/")
async def languages(
    current_user: steins_feed_api.auth.UserDep,
) -> list[steins_feed_model.feeds.Language]:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.feeds.Feed.language,
    ).join(
        steins_feed_model.feeds.Feed.users,
    ).where(
        steins_feed_model.users.User.id == current_user.id,
    ).order_by(
        steins_feed_model.feeds.Feed.language,
    ).distinct()

    with sqla_orm.Session(engine) as session:
        return [
            lang_it
            for lang_it in session.execute(q).scalars()
            if lang_it is not None
        ]

@router.get("/feed/{feed_id}")
async def feed(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
) -> Feed:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).where(
        steins_feed_model.feeds.Feed.id == feed_id,
    ).options(
        sqla_orm.joinedload(
            steins_feed_model.feeds.Feed.tags.and_(
                steins_feed_model.feeds.Tag.user_id == current_user.id,
            ),
        ),
        sqla_orm.joinedload(
            steins_feed_model.feeds.Feed.users.and_(
                steins_feed_model.users.User.id == current_user.id,
            ),
        ),
    )

    with sqla_orm.Session(engine) as session:
        return Feed.from_model(session.execute(q).scalars().unique().one())
