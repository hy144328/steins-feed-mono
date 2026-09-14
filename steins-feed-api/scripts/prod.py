#!/usr/bin/env python3

import logging
import logging.config
import tomllib

import dotenv
import uvicorn

dotenv.load_dotenv()

with open("logging.toml", "rb") as f:
    logging.config.dictConfig(tomllib.load(f))

if __name__ == "__main__":
    uvicorn.run(
        "steins_feed_api:app",
        log_level=logging.INFO,
    )
