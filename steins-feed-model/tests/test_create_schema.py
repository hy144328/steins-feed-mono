import pytest
import sqlalchemy as sqla

import steins_feed_model
import steins_feed_model.base

@pytest.fixture
def engine() -> sqla.engine.Engine:
    return steins_feed_model.EngineFactory.create_engine()

def test_create_schema(engine: sqla.engine.Engine):
    steins_feed_model.base.Base.metadata.create_all(engine)
    metadata = steins_feed_model.EngineFactory.create_metadata(engine)

    assert "User" in metadata.tables
    assert "Role" in metadata.tables

    assert "Feed" in metadata.tables
    assert "Display" in metadata.tables
    assert "Tag" in metadata.tables

    assert "Item" in metadata.tables
    assert "Like" in metadata.tables
    assert "Magic" in metadata.tables
