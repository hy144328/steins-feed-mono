import enum

import sqlalchemy as sqla

from . import feeds, types, users
from ..orm import base

class Like(enum.Enum):
    UP = 1
    MEH = 0
    DOWN = -1

t_items = sqla.Table(
    "Items",
    base.Base.metadata,
    sqla.Column("ItemID", sqla.Integer, primary_key=True),
    sqla.Column("Title", types.TEXT, nullable=False),
    sqla.Column("Link", types.TEXT, nullable=False),
    sqla.Column("Published", sqla.DateTime, nullable=False),
    sqla.Column("FeedID", sqla.Integer, types.ForeignKey(feeds.t_feeds.c.FeedID), nullable=False),
    sqla.Column("Summary", types.MEDIUMTEXT),
    sqla.UniqueConstraint("Title", "Published", "FeedID"),
)

t_likes = sqla.Table(
    "Like",
    base.Base.metadata,
    sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.t_users.c.UserID), nullable=False),
    sqla.Column("ItemID", sqla.Integer, types.ForeignKey(t_items.c.ItemID), nullable=False),
    sqla.Column("Score", sqla.Enum(Like), nullable=False),
    sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
    sqla.Column("Updated", sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now()),
    sqla.UniqueConstraint("UserID", "ItemID"),
)

t_magic = sqla.Table(
    "Magic",
    base.Base.metadata,
    sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.t_users.c.UserID), nullable=False),
    sqla.Column("ItemID", sqla.Integer, types.ForeignKey(t_items.c.ItemID), nullable=False),
    sqla.Column("Score", sqla.Float, nullable=False),
    sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
    sqla.Column("Updated", sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now()),
    sqla.UniqueConstraint("UserID", "ItemID"),
    sqla.CheckConstraint(
        "Score BETWEEN {} AND {}".format(Like.DOWN.value, Like.UP.value)
    ),
)

def create_schema(conn: sqla.Connection):
    t_items.create(conn, checkfirst=True)
    t_likes.create(conn, checkfirst=True)
    t_magic.create(conn, checkfirst=True)
