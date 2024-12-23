import sqlalchemy.orm as sqla_orm

class Base(sqla_orm.MappedAsDataclass, sqla_orm.DeclarativeBase):
    pass
