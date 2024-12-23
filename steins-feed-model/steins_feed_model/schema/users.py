import sqlalchemy as sqla

from . import types
from ..orm import base

t_users = sqla.Table(
    "Users",
    base.Base.metadata,
    sqla.Column("UserID", sqla.Integer, primary_key=True),
    sqla.Column("Name", types.TINYTEXT, nullable=False, unique=True),
    sqla.Column("Password", types.TINYTEXT, nullable=False),
    sqla.Column("Email", types.TINYTEXT, nullable=False, unique=True),
    sqla.Column("Active", sqla.Boolean, nullable=False),
)

t_roles = sqla.Table(
    "Roles",
    base.Base.metadata,
    sqla.Column("RoleID", sqla.Integer, primary_key=True),
    sqla.Column("Name", types.TINYTEXT, nullable=False, unique=True),
    sqla.Column("Description", types.TEXT),
)

t_users2roles = sqla.Table(
    "Users2Roles",
    base.Base.metadata,
    sqla.Column("UserID", sqla.Integer, types.ForeignKey(t_users.c.UserID), nullable=False),
    sqla.Column("RoleID", sqla.Integer, types.ForeignKey(t_roles.c.RoleID), nullable=False),
    sqla.UniqueConstraint("UserID", "RoleID"),
)

def create_schema(conn: sqla.Connection):
    t_users.create(conn, checkfirst=True)
    t_roles.create(conn, checkfirst=True)
    t_users2roles.create(conn, checkfirst=True)
