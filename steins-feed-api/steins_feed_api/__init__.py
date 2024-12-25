#!/usr/bin/env python3

import os

import dotenv
import fastapi

import steins_feed_model

import steins_feed_api.routers.items

dotenv.load_dotenv()

engine = steins_feed_model.EngineFactory.get_or_create_engine(
    username = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    database = os.getenv("DB_NAME"),
)

app = fastapi.FastAPI()

app.include_router(steins_feed_api.routers.items.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
