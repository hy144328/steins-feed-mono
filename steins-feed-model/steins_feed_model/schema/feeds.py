import enum

import sqlalchemy as sqla

from . import types

class Language(enum.Enum):
    ENGLISH = "English"
    GERMAN = "German"
    SWEDISH = "Swedish"

def create_schema(
    conn: sqla.Connection,
    meta: sqla.MetaData,
):
    users = meta.tables["Users"]

    # Feeds.
    feeds = sqla.Table(
        "Feeds",
        meta,
        sqla.Column("FeedID", sqla.Integer, primary_key=True),
        sqla.Column("Title", types.TEXT, nullable=False, unique=True),
        sqla.Column("Link", types.TEXT, nullable=False, unique=True),
        sqla.Column("Language", sqla.Enum(Language)),
        sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
        sqla.Column("Updated", sqla.DateTime),
    )
    feeds.create(conn, checkfirst=True)

    # Display.
    display = sqla.Table(
        "Display",
        meta,
        sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.c.UserID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, types.ForeignKey(feeds.c.FeedID), nullable=False),
        sqla.UniqueConstraint("UserID", "FeedID"),
    )
    display.create(conn, checkfirst=True)

    # Tags.
    tags = sqla.Table(
        "Tags",
        meta,
        sqla.Column("TagID", sqla.Integer, primary_key=True),
        sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.c.UserID), nullable=False),
        sqla.Column("Name", types.TINYTEXT, nullable=False),
        sqla.UniqueConstraint("UserID", "Name"),
    )
    tags.create(conn, checkfirst=True)

    # Many-to-many relationship.
    tags2feeds = sqla.Table(
        "Tags2Feeds",
        meta,
        sqla.Column("TagID", sqla.Integer, types.ForeignKey(tags.c.TagID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, types.ForeignKey(feeds.c.FeedID), nullable=False),
        sqla.UniqueConstraint("TagID", "FeedID"),
    )
    tags2feeds.create(conn, checkfirst=True)
