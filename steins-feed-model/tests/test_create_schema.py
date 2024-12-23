import sqlalchemy as sqla
import pytest

import steins_feed_model
import steins_feed_model.schema

@pytest.fixture
def engine() -> sqla.engine.Engine:
    return steins_feed_model.EngineFactory.get_or_create_engine()

def test_create_schema(engine: sqla.engine.Engine):
    with engine.connect() as conn:
        steins_feed_model.schema.create_schema(conn)
        metadata = steins_feed_model.EngineFactory.create_metadata(engine)

    assert "Users" in metadata.tables
    assert "Roles" in metadata.tables

    assert "Feeds" in metadata.tables
    assert "Display" in metadata.tables
    assert "Tags" in metadata.tables

    assert "Items" in metadata.tables
    assert "Like" in metadata.tables
    assert "Magic" in metadata.tables
