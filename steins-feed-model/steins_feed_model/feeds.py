import enum
import typing

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from . import base, types, users

class Language(enum.Enum):
    ENGLISH = "English"
    GERMAN = "German"
    SWEDISH = "Swedish"

class Feed(base.Base):
    __tablename__ = "Feed"

    id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, primary_key=True, init=False)
    title: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TEXT, unique=True)
    link: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TEXT, unique=True)
    language: sqla_orm.Mapped[typing.Optional[Language]] = sqla_orm.mapped_column(sqla.Enum(Language), default=None)

    users: sqla_orm.Mapped[list["users.User"]] = sqla_orm.relationship(
        "User",
        secondary="Display",
        #back_populates="feeds",
        init=False,
    )
    tags: sqla_orm.Mapped[list["Tag"]] = sqla_orm.relationship(
        "Tag",
        secondary="Tag2Feed",
        back_populates="feeds",
        init=False,
    )

class Tag(base.Base):
    __tablename__ = "Tag"
    __table_args__ = (
        sqla.UniqueConstraint("user_id", "name"),
    )

    id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, primary_key=True, init=False)
    user_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(users.User.id))
    name: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TINYTEXT)

    feeds: sqla_orm.Mapped[list["Feed"]] = sqla_orm.relationship(
        "Feed",
        secondary="Tag2Feed",
        back_populates="tags",
        init=False,
    )
    user: sqla_orm.Mapped["users.User"] = sqla_orm.relationship(
        "User",
        init=False,
    )

sqla.Table(
    "Display",
    base.Base.metadata,
    sqla.Column("user_id", sqla.Integer, types.ForeignKey(users.User.id), nullable=False),
    sqla.Column("feed_id", sqla.Integer, types.ForeignKey(Feed.id), nullable=False),
    sqla.UniqueConstraint("user_id", "feed_id"),
)

sqla.Table(
    "Tag2Feed",
    base.Base.metadata,
    sqla.Column("tag_id", sqla.Integer, types.ForeignKey(Tag.id), nullable=False),
    sqla.Column("feed_id", sqla.Integer, types.ForeignKey(Feed.id), nullable=False),
    sqla.UniqueConstraint("tag_id", "feed_id"),
)
