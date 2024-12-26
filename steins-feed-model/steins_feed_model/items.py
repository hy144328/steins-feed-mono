import datetime
import enum
import typing

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from . import base, feeds, types, users

class LikeStatus(int, enum.Enum):
    UP = 1
    MEH = 0
    DOWN = -1

class Item(base.Base):
    __tablename__ = "Item"
    __table_args__ = (
        sqla.UniqueConstraint("published", "title", "feed_id"),
    )

    id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, primary_key=True, init=False)
    title: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TEXT)
    link: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TEXT)
    published: sqla_orm.Mapped[datetime.datetime] = sqla_orm.mapped_column(sqla.DateTime)
    feed_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(feeds.Feed.id))
    summary: sqla_orm.Mapped[typing.Optional[str]] = sqla_orm.mapped_column(types.MEDIUMTEXT, default=None)

    feed: sqla_orm.Mapped["feeds.Feed"] = sqla_orm.relationship(
        "Feed",
        #back_populates="items",
        init=False,
    )
    likes: sqla_orm.Mapped[list["Like"]] = sqla_orm.relationship(
        "Like",
        back_populates="item",
        init=False,
    )
    magic: sqla_orm.Mapped[list["Magic"]] = sqla_orm.relationship(
        "Magic",
        back_populates="item",
        init=False,
    )

class Like(base.Base):
    __tablename__ = "Like"
    __table_args__ = (
        sqla.UniqueConstraint("user_id", "item_id"),
    )
    __mapper_args__ = {
        "primary_key": ["user_id", "item_id"],
    }

    user_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(users.User.id))
    item_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(Item.id))
    score: sqla_orm.Mapped[LikeStatus] = sqla_orm.mapped_column(sqla.Enum(LikeStatus))
    added: sqla_orm.Mapped[datetime.datetime] = sqla_orm.mapped_column(sqla.DateTime, server_default=sqla.func.now(), init=False)
    updated: sqla_orm.Mapped[datetime.datetime] = sqla_orm.mapped_column(sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now(), init=False)

    user: sqla_orm.Mapped["users.User"] = sqla_orm.relationship(
        "User",
        #back_populates="likes",
        init=False,
    )
    item: sqla_orm.Mapped["Item"] = sqla_orm.relationship(
        "Item",
        back_populates="likes",
        init=False,
    )

class Magic(base.Base):
    __tablename__ = "Magic"
    __table_args__ = (
        sqla.UniqueConstraint("user_id", "item_id"),
        sqla.CheckConstraint(f"score BETWEEN {LikeStatus.DOWN.value} AND {LikeStatus.UP.value}"),
    )
    __mapper_args__ = {
        "primary_key": ["user_id", "item_id"],
    }

    user_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(users.User.id))
    item_id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, types.ForeignKey(Item.id))
    score: sqla_orm.Mapped[float] = sqla_orm.mapped_column("Score", sqla.Float)
    added: sqla_orm.Mapped[datetime.datetime] = sqla_orm.mapped_column(sqla.DateTime, server_default=sqla.func.now())
    updated: sqla_orm.Mapped[datetime.datetime] = sqla_orm.mapped_column(sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now())

    user: sqla_orm.Mapped["users.User"] = sqla_orm.relationship(
        "User",
        #back_populates="magic",
        init=False,
    )
    item: sqla_orm.Mapped["Item"] = sqla_orm.relationship(
        "Item",
        back_populates="magic",
        init=False,
    )
