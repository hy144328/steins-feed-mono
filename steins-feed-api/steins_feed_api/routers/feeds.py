import typing

import fastapi
import pydantic
import sqlalchemy as sqla
import sqlalchemy.exc as sqla_exc
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
    displayed: bool

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

    with sqla_orm.Session(engine) as session:
        feed = session.get(
            steins_feed_model.feeds.Feed,
            feed_id,
            options = [
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.users.and_(
                        steins_feed_model.users.User.id == current_user.id,
                    ),
                ),
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.tags.and_(
                        steins_feed_model.feeds.Tag.user_id == current_user.id,
                    ),
                ),
            ],
        )
        assert feed is not None

        return Feed.from_model(feed)

@router.put("/feed/{feed_id}/attach_tag")
async def attach_tag(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
    tag_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    with sqla_orm.Session(engine) as session:
        feed = session.get(
            steins_feed_model.feeds.Feed,
            feed_id,
            options = [
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.tags.and_(
                        steins_feed_model.feeds.Tag.user_id == current_user.id,
                    ),
                ),
            ],
        )
        assert feed is not None

        tag = session.get(
            steins_feed_model.feeds.Tag,
            tag_id,
        )
        assert tag is not None

        try:
            feed.tags.append(tag)
            session.commit()
            logger.info(f"Successfully added feed #{feed_id} to user #{current_user.id}'s tag #{tag_id}.")
        except sqla_exc.IntegrityError:
            logger.warning(f"Feed #{feed_id} already belongs to user #{current_user.id}'s tag #{tag_id}.")

@router.delete("/feed/{feed_id}/detach_tag")
async def detach_tag(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
    tag_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    with sqla_orm.Session(engine) as session:
        feed = session.get(
            steins_feed_model.feeds.Feed,
            feed_id,
            options = [
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.tags.and_(
                        steins_feed_model.feeds.Tag.user_id == current_user.id,
                    ),
                ),
            ],
        )
        assert feed is not None

        tag = session.get(
            steins_feed_model.feeds.Tag,
            tag_id,
        )
        assert tag is not None

        try:
            feed.tags.remove(tag)
            session.commit()
            logger.info(f"Successfully removed feed #{feed_id} from user #{current_user.id}'s tag #{tag_id}.")
        except ValueError:
            logger.warning(f"Feed #{feed_id} does not belong to user #{current_user.id}'s tag #{tag_id}.")

@router.put("/feed/{feed_id}/create_and_attach_tag")
async def create_and_attach_tag(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
    tag_name: str,
) -> Tag:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    tag = steins_feed_model.feeds.Tag(
        user_id = current_user.id,
        name = tag_name,
    )

    q = sqla.select(
        steins_feed_model.feeds.Tag,
    ).where(
        steins_feed_model.feeds.Tag.user_id == current_user.id,
        steins_feed_model.feeds.Tag.name == tag_name,
    )

    with sqla_orm.Session(engine) as session:
        try:
            session.add(tag)
            session.commit()
            logger.info(f"Successfully created user {current_user.name}'s tag {tag_name}.")
        except sqla_exc.IntegrityError:
            logger.warning(f"User {current_user.name}'s tag {tag_name} already exists.")
            session.rollback()
            tag = session.execute(q).scalars().one()

        tag_id = tag.id
        res = Tag.from_model(tag)

    await attach_tag(current_user, feed_id, tag_id)
    return res

@router.put("/feed/{feed_id}/attach_user")
async def attach_user(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    with sqla_orm.Session(engine) as session:
        feed = session.get(
            steins_feed_model.feeds.Feed,
            feed_id,
            options = [
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.users.and_(
                        steins_feed_model.users.User.id == current_user.id,
                    ),
                ),
            ],
        )
        assert feed is not None

        user = session.get(
            steins_feed_model.users.User,
            current_user.id,
        )
        assert user is not None

        try:
            feed.users.append(user)
            session.commit()
            logger.info(f"Successfully added to user #{current_user.id} to feed #{feed_id}.")
        except sqla_exc.IntegrityError:
            logger.warning(f"User #{current_user.id} already belongs to feed #{feed_id}.")

@router.delete("/feed/{feed_id}/detach_user")
async def detach_user(
    current_user: steins_feed_api.auth.UserDep,
    feed_id: int,
):
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    with sqla_orm.Session(engine) as session:
        feed = session.get(
            steins_feed_model.feeds.Feed,
            feed_id,
            options = [
                sqla_orm.joinedload(
                    steins_feed_model.feeds.Feed.users.and_(
                        steins_feed_model.users.User.id == current_user.id,
                    ),
                ),
            ],
        )
        assert feed is not None

        user = session.get(
            steins_feed_model.users.User,
            current_user.id,
        )
        assert user is not None

        try:
            feed.users.remove(user)
            session.commit()
            logger.info(f"Successfully removed user #{current_user.id} from feed #{feed_id}.")
        except ValueError:
            logger.warning(f"User #{current_user.id}'s does not belong to feed #{feed_id}.")
