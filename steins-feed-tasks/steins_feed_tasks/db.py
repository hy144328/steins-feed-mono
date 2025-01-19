import os

import steins_feed_model

engine = steins_feed_model.EngineFactory.get_or_create_engine(database=os.environ["DB_NAME"])
