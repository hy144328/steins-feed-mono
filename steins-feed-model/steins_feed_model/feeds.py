import typing

import lxml.etree
import sqlalchemy as sqla

import steins_feed_model.schema.feeds

def read_xml(
    conn: sqla.Connection,
    meta: sqla.MetaData,
    f: typing.IO,
    user_id: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
):
    t_feeds = meta.tables["Feeds"]
    t_tags2feeds = meta.tables["Tags2Feeds"]
    t_tags = meta.tables["Tags"]

    tree = lxml.etree.parse(f)
    root = tree.getroot()

    rows = [
        {
            "Title": feed_it.xpath("title")[0].text,
            "Link": feed_it.xpath("link")[0].text,
            "Language": steins_feed_model.schema.feeds.Language(feed_it.xpath("lang")[0].text).name,
        }
        for feed_it in root.xpath("feed")
    ]

    q = t_feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    with conn.begin():
        conn.execute(q, rows)

    if user_id and tag:
        q = t_tags.insert().values(
            UserID=user_id,
            Name=tag,
        )
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        with conn.begin():
            conn.execute(q)

        q_select = sqla.select(
            t_feeds.c.FeedID,
            t_tags.c.TagID,
        ).where(sqla.and_(
            t_feeds.c.Title == sqla.bindparam("Title"),
            t_tags.c.UserID == user_id,
            t_tags.c.Name == tag,
        ))

        q = t_tags2feeds.insert()
        q = q.from_select([q_select.c.FeedID, q_select.c.TagID], q_select)
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        with conn.begin():
            conn.execute(q, rows)

def write_xml(
    conn: sqla.Connection,
    meta: sqla.MetaData,
    f: typing.IO,
    user_id: typing.Optional[str] = None,
    tag: typing.Optional[str] = None,
):
    t_feeds = meta.tables["Feeds"]
    t_tags2feeds = meta.tables["Tags2Feeds"]
    t_tags = meta.tables["Tags"]

    q = sqla.select(t_feeds)
    if user_id and tag:
        q = q.select_from(
            t_feeds.join(t_tags2feeds)
                   .join(t_tags)
        )
        q = q.where(sqla.and_(
            t_tags.c.UserID == user_id,
            t_tags.c.Name == tag,
        ))
    q = q.order_by(sqla.collate(t_feeds.c.Title, "NOCASE"))

    with conn.begin():
        rows = conn.execute(q).mappings().fetchall()

    root = lxml.etree.Element("root")
    for row_it in rows:
        title_it = lxml.etree.Element("title")
        title_it.text = row_it["Title"]

        link_it = lxml.etree.Element("link")
        link_it.text = row_it["Link"]

        lang_it = lxml.etree.Element("lang")
        lang_it.text = steins_feed_model.schema.feeds.Language[row_it["Language"]].value

        feed_it = lxml.etree.Element("feed")
        feed_it.append(title_it)
        feed_it.append(link_it)
        feed_it.append(lang_it)

        root.append(feed_it)

    s = lxml.etree.tostring(
        root,
        encoding="unicode",
        pretty_print=True,
    )
    f.write(s)
