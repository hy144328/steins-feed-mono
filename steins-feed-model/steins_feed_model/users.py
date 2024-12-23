import typing

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from . import base, types

class User(base.Base):
    __tablename__ = "User"

    id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, primary_key=True, init=False)
    name: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TINYTEXT, unique=True)
    password: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TINYTEXT)
    email: sqla_orm.Mapped[str] = sqla_orm.mapped_column("email", types.TINYTEXT, unique=True)

    roles: sqla_orm.Mapped[list["Role"]] = sqla_orm.relationship(
        "Role",
        secondary="User2Role",
        back_populates="users",
        init=False,
    )

class Role(base.Base):
    __tablename__ = "Role"

    id: sqla_orm.Mapped[int] = sqla_orm.mapped_column(sqla.Integer, primary_key=True, init=False)
    name: sqla_orm.Mapped[str] = sqla_orm.mapped_column(types.TINYTEXT, unique=True)
    description: sqla_orm.Mapped[typing.Optional[str]] = sqla_orm.mapped_column(types.TEXT, default=None)

    users: sqla_orm.Mapped[list["User"]] = sqla_orm.relationship(
        "User",
        secondary="User2Role",
        back_populates="roles",
        init=False,
    )

sqla.Table(
    "User2Role",
    base.Base.metadata,
    sqla.Column("user_id", sqla.Integer, types.ForeignKey(User.id), nullable=False),
    sqla.Column("role_id", sqla.Integer, types.ForeignKey(Role.id), nullable=False),
    sqla.UniqueConstraint("user_id", "role_id"),
)
