#!/usr/bin/env python3

import os

import dotenv

import steins_feed_model
import steins_feed_model.base

dotenv.load_dotenv()

engine = steins_feed_model.EngineFactory.get_or_create_engine(database=os.environ["DB_NAME"])
steins_feed_model.base.Base.metadata.create_all(engine)
