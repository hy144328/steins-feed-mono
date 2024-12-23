import sqlalchemy as sqla

from . import types

def create_schema(
    conn: sqla.Connection,
    meta: sqla.MetaData,
):
    # Users.
    users = sqla.Table(
        "Users",
        meta,
        sqla.Column("UserID", sqla.Integer, primary_key=True),
        sqla.Column("Name", types.TINYTEXT, nullable=False, unique=True),
        sqla.Column("Password", types.TINYTEXT, nullable=False),
        sqla.Column("Email", types.TINYTEXT, nullable=False, unique=True),
        sqla.Column("Active", sqla.Boolean, nullable=False),
    )
    users.create(conn, checkfirst=True)

    # Roles.
    roles = sqla.Table(
        "Roles",
        meta,
        sqla.Column("RoleID", sqla.Integer, primary_key=True),
        sqla.Column("Name", types.TINYTEXT, nullable=False, unique=True),
        sqla.Column("Description", types.TEXT),
    )
    roles.create(conn, checkfirst=True)

    # Many-to-many relationship.
    users2roles = sqla.Table(
        "Users2Roles",
        meta,
        sqla.Column("UserID", sqla.Integer, types.ForeignKey(users.c.UserID), nullable=False),
        sqla.Column("RoleID", sqla.Integer, types.ForeignKey(roles.c.RoleID), nullable=False),
        sqla.UniqueConstraint("UserID", "RoleID"),
    )
    users2roles.create(conn, checkfirst=True)
