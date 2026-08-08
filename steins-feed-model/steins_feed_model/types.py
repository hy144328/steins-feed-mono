import typing

import sqlalchemy as sqla

if typing.TYPE_CHECKING:    # pragma: no cover
    import sqlalchemy.sql._typing as sqla_typing

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

def create_foreign_key(
    column: "sqla_typing._DDLColumnArgument",
    on_update: str | None = None,
    on_delete: str | None = None,
) -> sqla.ForeignKey:
    return sqla.ForeignKey(
        column = column,
        onupdate = on_update or "CASCADE",
        ondelete = on_delete or "CASCADE",
    )
