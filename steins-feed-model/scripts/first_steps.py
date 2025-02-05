#!/usr/bin/env python3

import os

import dotenv

import steins_feed_model
import steins_feed_model.base

dotenv.load_dotenv()

engine = steins_feed_model.EngineFactory.create_engine(
    username = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    database = os.getenv("DB_NAME"),
)
steins_feed_model.base.Base.metadata.create_all(engine)
