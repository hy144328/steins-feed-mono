import logging
import typing

import lxml.etree
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm

import steins_feed_config.db
import steins_feed_model.feeds

logger = logging.getLogger(__name__)

def read_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_id: int | None,
):
    tree = lxml.etree.parse(f)
    root = tree.getroot()

    for feed_it in root.xpath("feed"):
        feed_title = feed_it.xpath("title")[0].text
        feed_link = feed_it.xpath("link")[0].text
        feed_lang = steins_feed_model.feeds.Language(feed_it.xpath("lang")[0].text)

        try:
            with session.begin():
                feed = steins_feed_config.db.create_feed(
                    session,
                    title = feed_title,
                    link = feed_link,
                    language = feed_lang,
                )
                logger.info(f"Create {feed_title}.")
        except sqla_exc.IntegrityError:
            logger.warning(f"Feed {feed_title} already exists.")
            continue

        if user_id is None:
            continue

        with session.begin():
            user = session.get_one(steins_feed_model.users.User, user_id)
            user_name = user.name

        try:
            with session.begin():
                feed.users.append(user)
                logger.info(f"Add {user_name} to display {feed_title}.")
        except sqla_exc.IntegrityError:
            logger.warning(f"{feed_title} already displayed to {user_name}.")

        for tag_it in feed_it.xpath("tag"):
            tag_name = tag_it.text

            try:
                with session.begin():
                    tag = steins_feed_config.db.get_tag(
                        session,
                        user_id = user_id,
                        tag_name = tag_name,
                    )
            except sqla_exc.NoResultFound:
                with session.begin():
                    tag = steins_feed_config.db.create_tag(
                        session,
                        user_id = user_id,
                        tag_name = tag_name,
                    )
                    logger.info(f"Create {tag_name}.")

            try:
                with session.begin():
                    feed.tags.append(tag)
                    logger.info(f"Add {tag_name} to {feed_title}.")
            except sqla_exc.IntegrityError:
                logger.warning(f"{feed_title} already in {tag_name}.")

def write_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_id: int | None,
):
    feeds = steins_feed_config.db.get_feeds(session)
    root = lxml.etree.Element("root")

    for feed_it in feeds:
        node_it = lxml.etree.Element("feed")

        title_it = lxml.etree.Element("title")
        title_it.text = feed_it.title
        node_it.append(title_it)

        link_it = lxml.etree.Element("link")
        link_it.text = feed_it.link
        node_it.append(link_it)

        lang_it = lxml.etree.Element("lang")
        lang_it.text = feed_it.language.value if feed_it.language is not None else None
        node_it.append(lang_it)

        for tag_it in feed_it.tags:
            if tag_it.user_id != user_id:
                continue

            tag_node_it = lxml.etree.Element("tag")
            tag_node_it.text = tag_it.name
            node_it.append(tag_node_it)

        root.append(node_it)

    s = lxml.etree.tostring(
        root,
        encoding = "unicode",
        pretty_print = True,
    )
    f.write(s)
