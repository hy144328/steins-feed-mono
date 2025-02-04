#!/usr/bin/env python3

import dotenv
import os

import sqlalchemy.orm as sqla_orm

import steins_feed_magic.classify
import steins_feed_magic.db
import steins_feed_magic.io
import steins_feed_model.feeds
import steins_feed_model.items
import steins_feed_magic.parse

dotenv.load_dotenv()

engine = steins_feed_model.EngineFactory.create_engine(database=os.environ["DB_NAME"])

user_id = 1
lang = steins_feed_model.feeds.Language.ENGLISH
clf = steins_feed_magic.classify.build_classifier(lang)

with sqla_orm.Session(engine) as session:
    liked_items = [
        steins_feed_magic.parse.text_content(item_it.title)
        for item_it in steins_feed_magic.db.liked_items(session, user_id, lang)
    ]
    disliked_items = [
        steins_feed_magic.parse.text_content(item_it.title)
        for item_it in steins_feed_magic.db.disliked_items(session, user_id, lang)
    ]

    steins_feed_magic.classify.fit_classifier(
        clf,
        liked_items = liked_items,
        disliked_items = disliked_items,
    )

    steins_feed_magic.io.write_classifier(clf, user_id, lang, force=True)
    clf = steins_feed_magic.io.read_classifier(user_id, lang)

    liked_scores = steins_feed_magic.classify.predict_scores(clf, liked_items)
    disliked_scores = steins_feed_magic.classify.predict_scores(clf, disliked_items)

    for item_it, score_it in zip(liked_items, liked_scores):
        print(f"{1:+d}", f"{score_it:+.3f}", item_it)

    for item_it, score_it in zip(disliked_items, disliked_scores):
        print(f"{-1:+d}", f"{score_it:+.3f}", item_it)
