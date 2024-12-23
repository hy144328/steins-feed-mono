import enum

import sqlalchemy as sqla

from . import types, users
from ..orm import base

class Language(enum.Enum):
    ENGLISH = "English"
    GERMAN = "German"
    SWEDISH = "Swedish"

t_feeds = sqla.Table(
    "Feeds",
    base.Base.metadata,
    sqla.Column("FeedID", sqla.Integer, primary_key=True),
    sqla.Column("Title", types.TEXT, nullable=False, unique=True),
    sqla.Column("Link", types.TEXT, nullable=False, unique=True),
    sqla.Column("Language", sqla.Enum(Language)),
)

t_display = sqla.Table(
    "Display",
    base.Base.metadata,
    sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.t_users.c.UserID), nullable=False),
    sqla.Column("FeedID", sqla.Integer, types.ForeignKey(t_feeds.c.FeedID), nullable=False),
    sqla.UniqueConstraint("UserID", "FeedID"),
)

t_tags = sqla.Table(
    "Tags",
    base.Base.metadata,
    sqla.Column("TagID", sqla.Integer, primary_key=True),
    sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.t_users.c.UserID), nullable=False),
    sqla.Column("Name", types.TINYTEXT, nullable=False),
    sqla.UniqueConstraint("UserID", "Name"),
)

t_tags2feeds = sqla.Table(
    "Tags2Feeds",
    base.Base.metadata,
    sqla.Column("TagID", sqla.Integer, types.ForeignKey(t_tags.c.TagID), nullable=False),
    sqla.Column("FeedID", sqla.Integer, types.ForeignKey(t_feeds.c.FeedID), nullable=False),
    sqla.UniqueConstraint("TagID", "FeedID"),
)

def create_schema(conn: sqla.Connection):
    t_feeds.create(conn, checkfirst=True)
    t_display.create(conn, checkfirst=True)
    t_tags.create(conn, checkfirst=True)
    t_tags2feeds.create(conn, checkfirst=True)
