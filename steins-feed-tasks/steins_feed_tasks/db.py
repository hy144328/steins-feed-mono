import os

import steins_feed_model

engine = steins_feed_model.EngineFactory.create_engine(
    username = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    database = os.environ["DB_NAME"],
)
