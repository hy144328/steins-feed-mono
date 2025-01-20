import logging
import os

import steins_feed_logging

try:
    os.mkdir("logs.d")
except FileExistsError:
    pass

with open("logs.d/steins_feed_etl.log", "a") as f:
    etl_logger = steins_feed_logging.LoggerFactory.get_logger("steins_feed_etl.items")
    steins_feed_logging.LoggerFactory.add_file_handler(etl_logger, f)
    steins_feed_logging.LoggerFactory.set_level(etl_logger, level=logging.INFO)

with open("logs.d/steins_feed_magic.log", "a") as f:
    magic_logger = steins_feed_logging.LoggerFactory.get_logger("steins_feed_magic")
    steins_feed_logging.LoggerFactory.add_file_handler(magic_logger, f)
    steins_feed_logging.LoggerFactory.set_level(magic_logger, level=logging.INFO)
