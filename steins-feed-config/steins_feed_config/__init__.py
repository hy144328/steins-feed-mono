import logging
import typing

import lxml.etree
import sqlalchemy.orm as sqla_orm

import steins_feed_config.db
import steins_feed_model.feeds

logger = logging.getLogger(__name__)

def read_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_name: str,
):
    user = steins_feed_config.db.get_user(
        session,
        user_name = user_name,
    )

    tree = lxml.etree.parse(f)
    root = tree.getroot()

    for feed_it in root.xpath("feed"):
        feed = steins_feed_config.db.get_or_create_feed(
            session,
            title = feed_it.xpath("title")[0].text,
            link = feed_it.xpath("link")[0].text,
            language = steins_feed_model.feeds.Language(feed_it.xpath("lang")[0].text),
        )

        for tag_it in feed_it.xpath("tag"):
            tag = steins_feed_config.db.get_or_create_tag(
                session,
                user = user,
                tag_name = tag_it.text,
            )
            steins_feed_config.db.add_tag(
                session,
                feed = feed,
                tag = tag,
            )

def write_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_name: str,
):
    root = lxml.etree.Element("root")

    user = steins_feed_config.db.get_user(
        session,
        user_name = user_name,
    )
    feeds = steins_feed_config.db.get_feeds(
        session,
        user = user,
    )

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
