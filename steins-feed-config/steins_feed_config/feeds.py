import typing

import lxml.etree
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model.feeds

def read_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_name: typing.Optional[str] = None,
    tag_name: typing.Optional[str] = None,
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
    session.commit()

    if user_name:
        q = sqla.select(
            steins_feed_model.users.User,
        ).where(
            steins_feed_model.users.User.name == user_name,
        )
        user = session.execute(q).scalars().one()

        q = sqla.select(
            steins_feed_model.feeds.Feed,
        ).where(
            steins_feed_model.feeds.Feed.title == sqla.bindparam("title"),
        )

        for feed_it in feeds:
            feed = session.execute(
                q,
                {"title": feed_it.title},
            ).scalars().one()

            if user not in feed.users:
                feed.users.append(user)
                session.commit()

        if tag_name:
            q = sqla.insert(
                steins_feed_model.feeds.Tag,
            ).values(
                user_id=user.id,
                name=tag_name,
            )
            q = q.prefix_with("OR IGNORE", dialect="sqlite")

            session.execute(q)
            session.commit()

            q = sqla.select(
                steins_feed_model.feeds.Tag,
            ).where(
                steins_feed_model.feeds.Tag.user_id == user.id,
                steins_feed_model.feeds.Tag.name == tag_name,
            )
            tag = session.execute(q).scalars().one()

            q = sqla.select(
                steins_feed_model.feeds.Feed,
            ).where(
                steins_feed_model.feeds.Feed.title == sqla.bindparam("title"),
            )

            for feed_it in feeds:
                feed = session.execute(
                    q,
                    {"title": feed_it.title},
                ).scalars().one()

                if tag not in feed.tags:
                    feed.tags.append(tag)
                    session.commit()

def write_xml(
    session: sqla_orm.Session,
    f: typing.TextIO,
    user_name: typing.Optional[str] = None,
    tag_name: typing.Optional[str] = None,
):
    q = sqla.select(
        steins_feed_model.feeds.Feed,
    ).order_by(
        sqla.collate(steins_feed_model.feeds.Feed.title, "NOCASE"),
    )

    if user_name:
        q = q.where(
            steins_feed_model.feeds.Feed.users.any(
                steins_feed_model.users.User.name == user_name,
            ),
        )

        if tag_name:
            q = q.where(
                steins_feed_model.feeds.Feed.tags.any(
                    sqla.and_(
                        steins_feed_model.feeds.Tag.user.has(steins_feed_model.users.User.name == user_name),
                        steins_feed_model.feeds.Tag.name == tag_name,
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
