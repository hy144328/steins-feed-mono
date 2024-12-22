import typing

import sqlalchemy as sqla

if typing.TYPE_CHECKING:
    import sqlalchemy.sql._typing as sqla_typing
    import sqlalchemy.sql.schema as sqla_schema

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

class ForeignKey(sqla.ForeignKey):
    def __init__(
        self,
        column: sqla_typing._DDLColumnArgument,
        _constraint: typing.Optional[sqla_schema.ForeignKeyConstraint] = None,
        use_alter: bool = False,
        name: sqla_schema._ConstraintNameArgument = None,
        onupdate: typing.Optional[str] = None,
        ondelete: typing.Optional[str] = None,
        deferrable: typing.Optional[bool] = None,
        initially: typing.Optional[str] = None,
        link_to_name: bool = False,
        match: typing.Optional[str] = None,
        info: typing.Optional[sqla_typing._InfoType] = None,
        comment: typing.Optional[str] = None,
        _unresolvable: bool = False,
        **dialect_kw: typing.Any,
    ):
        super().__init__(
            column,
            _constraint,
            use_alter,
            name,
            onupdate or "CASCADE",
            ondelete or "CASCADE",
            deferrable,
            initially,
            link_to_name,
            match,
            info,
            comment,
            _unresolvable,
            **dialect_kw,
        )
