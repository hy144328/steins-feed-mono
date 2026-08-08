import pytest
import sqlalchemy as sqla

import steins_feed_model
import steins_feed_model.base

@pytest.fixture
def engine() -> sqla.Engine:
    res = sqla.create_engine(sqla.URL.create("sqlite"))
    steins_feed_model.base.Base.metadata.create_all(res)
    return res

@pytest.fixture
def metadata(engine: sqla.Engine) -> sqla.MetaData:
    res = sqla.MetaData()
    res.reflect(bind=engine)
    return res

def test_create_schema(metadata: sqla.MetaData):
    assert "User" in metadata.tables
    assert "Role" in metadata.tables

    assert "Feed" in metadata.tables
    assert "Display" in metadata.tables
    assert "Tag" in metadata.tables

    assert "Item" in metadata.tables
    assert "Like" in metadata.tables
    assert "Magic" in metadata.tables
