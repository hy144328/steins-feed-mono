import datetime

import fastapi
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

@router.get("/")
async def root(
    dt_from: datetime.datetime,
    dt_to: datetime.datetime,
) -> list[steins_feed_model.items.Item]:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    q = sqla.select(
        steins_feed_model.items.Item,
    ).where(
        steins_feed_model.items.Item.feed.has(
            steins_feed_model.feeds.Feed.users.any(
                steins_feed_model.users.User.name == "hansolo",
            ),
        ),
        steins_feed_model.items.Item.published >= dt_from,
        steins_feed_model.items.Item.published < dt_to,
    )

    with sqla_orm.Session(engine) as session:
        res = session.execute(q).scalars().all()
        return list(res)
