import typing

import lxml.etree
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model.feeds

def read_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_id: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
):
    tree = lxml.etree.parse(f)
    root = tree.getroot()

    feeds = [
        steins_feed_model.feeds.Feed(
            title = feed_it.xpath("title")[0].text,
            link = feed_it.xpath("link")[0].text,
            language = steins_feed_model.feeds.Language(feed_it.xpath("lang")[0].text),
        )
        for feed_it in root.xpath("feed")
    ]

    q = sqla.insert(steins_feed_model.feeds.Feed)
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    with session.begin():
        session.execute(
            q,
            [
                {
                    "title": feed_it.title,
                    "link": feed_it.link,
                    "language": feed_it.language,
                }
                for feed_it in feeds
            ],
        )

    if user_id and tag:
        q = sqla.insert(
            steins_feed_model.feeds.Tag,
        ).values(
            user_id=user_id,
            name=tag,
        )
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        tag_record = session.execute(q).scalars().one()

        q = sqla.select(
            steins_feed_model.feeds.Feed,
        ).where(
            steins_feed_model.feeds.Feed.title == sqla.bindparam("title"),
        )

        with session.begin():
            for feed_it in feeds:
                feed_record = session.execute(
                    q,
                    {"title": feed_it.title},
                ).scalars().one()

                if tag_record not in feed_record.tags:
                    feed_record.tags.append(tag_record)

def write_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_id: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
):
    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).order_by(
        sqla.collate(steins_feed_model.feeds.Feed.title, "NOCASE"),
    )
    if user_id and tag:
        q = q.where(
            steins_feed_model.feeds.Feed.tags.any(
                sqla.and_(
                    steins_feed_model.feeds.Tag.user_id == user_id,
                    steins_feed_model.feeds.Tag.name == tag,
                ),
            ),
        )

    feeds = session.execute(q).scalars().all()

    root = lxml.etree.Element("root")

    for feed_it in feeds:
        title_it = lxml.etree.Element("title")
        title_it.text = feed_it.title

        link_it = lxml.etree.Element("link")
        link_it.text = feed_it.link

        lang_it = lxml.etree.Element("lang")
        lang_it.text = feed_it.language.value if feed_it.language is not None else None

        node_it = lxml.etree.Element("feed")
        node_it.append(title_it)
        node_it.append(link_it)
        node_it.append(lang_it)

        root.append(node_it)

    s = lxml.etree.tostring(
        root,
        encoding="unicode",
        pretty_print=True,
    )
    f.write(s)
