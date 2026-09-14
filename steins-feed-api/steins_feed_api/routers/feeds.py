import logging

import fastapi
import pydantic
import sqlalchemy as sqla
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm

import steins_feed_model
import steins_feed_model.feeds
import steins_feed_model.users

from .. import auth, db

logger = logging.getLogger(__name__)

router = fastapi.APIRouter(
    prefix = "/feeds",
    tags = ["feeds"],
)

class Feed(pydantic.BaseModel):
    id: int
    title: str
    link: str
    language: steins_feed_model.feeds.Language | None
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
    session: db.SessionDep,
    current_user: auth.UserDep,
) -> list[Tag]:
    q = sqla.select(
        steins_feed_model.feeds.Tag,
    ).where(
        steins_feed_model.feeds.Tag.user_id == current_user.id,
    ).order_by(
        steins_feed_model.feeds.Tag.name,
    )

    return [
        Tag.from_model(tag_it)
        for tag_it in session.scalars(q)
    ]

@router.get("/languages/")
async def languages(
    session: db.SessionDep,
    current_user: auth.UserDep,
) -> list[steins_feed_model.feeds.Language]:
    q = sqla.select(
        steins_feed_model.feeds.Feed.language,
    ).join(
        steins_feed_model.feeds.Feed.users,
    ).where(
        steins_feed_model.users.User.id == current_user.id,
    ).order_by(
        steins_feed_model.feeds.Feed.language,
    ).distinct()

    return [
        lang_it
        for lang_it in session.scalars(q)
        if lang_it is not None
    ]

@router.get("/feed/{feed_id}")
async def feed(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
) -> Feed:
    feed = session.get_one(
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
    return Feed.from_model(feed)

@router.put("/feed/{feed_id}/attach_tag")
async def attach_tag(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
    tag_id: int,
):
    feed = session.get_one(
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
    tag = session.get_one(
        steins_feed_model.feeds.Tag,
        tag_id,
    )

    try:
        with session.begin():
            feed.tags.append(tag)
            logger.info(f"Successfully added feed #{feed_id} to user #{current_user.id}'s tag #{tag_id}.")
    except sqla_exc.IntegrityError:
        logger.warning(f"Feed #{feed_id} already belongs to user #{current_user.id}'s tag #{tag_id}.")

@router.delete("/feed/{feed_id}/detach_tag")
async def detach_tag(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
    tag_id: int,
):
    feed = session.get_one(
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
    tag = session.get_one(
        steins_feed_model.feeds.Tag,
        tag_id,
    )

    try:
        with session.begin():
            feed.tags.remove(tag)
            logger.info(f"Successfully removed feed #{feed_id} from user #{current_user.id}'s tag #{tag_id}.")
    except ValueError:
        logger.warning(f"Feed #{feed_id} does not belong to user #{current_user.id}'s tag #{tag_id}.")

@router.put("/feed/{feed_id}/create_and_attach_tag")
async def create_and_attach_tag(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
    tag_name: str,
) -> Tag:
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

    try:
        with session.begin():
            session.add(tag)
            logger.info(f"Successfully created user {current_user.name}'s tag {tag_name}.")
            res = Tag.from_model(tag)
    except sqla_exc.IntegrityError:
        with session.begin():
            tag = session.scalars(q).one()
            logger.warning(f"User {current_user.name}'s tag {tag_name} already exists.")
            res = Tag.from_model(tag)

    await attach_tag(session, current_user, feed_id, res.id)
    return res

@router.put("/feed/{feed_id}/attach_user")
async def attach_user(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
):
    feed = session.get_one(
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
    user = session.get_one(
        steins_feed_model.users.User,
        current_user.id,
    )

    try:
        with session.begin():
            feed.users.append(user)
            logger.info(f"Successfully added to user #{current_user.id} to feed #{feed_id}.")
    except sqla_exc.IntegrityError:
        logger.warning(f"User #{current_user.id} already belongs to feed #{feed_id}.")

@router.delete("/feed/{feed_id}/detach_user")
async def detach_user(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
):
    feed = session.get_one(
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
    user = session.get_one(
        steins_feed_model.users.User,
        current_user.id,
    )

    try:
        with session.begin():
            feed.users.remove(user)
            logger.info(f"Successfully removed user #{current_user.id} from feed #{feed_id}.")
    except ValueError:
        logger.warning(f"User #{current_user.id}'s does not belong to feed #{feed_id}.")

@router.post("/feed/{feed_id}/update_feed")
async def update_feed(
    session: db.SessionDep,
    current_user: auth.UserDep,
    feed_id: int,
    title: str,
    link: str,
    language: steins_feed_model.feeds.Language | None = None,
) -> Feed:
    if current_user.name != "hansolo":
        raise fastapi.HTTPException(
            status_code = fastapi.status.HTTP_401_UNAUTHORIZED,
            detail = "Not an admin.",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    with session.begin():
        feed = session.get_one(steins_feed_model.feeds.Feed, feed_id)

        feed.title = title
        feed.link = link
        feed.language = language

        return Feed.from_model(feed)
