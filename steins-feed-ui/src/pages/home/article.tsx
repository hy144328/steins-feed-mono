import { Collapse, Popover } from "bootstrap"
import DOMPurify from "dompurify"
import { Fragment, ReactNode } from "react"
import { useEffect, useRef, useState } from "react"
import { Link } from "react-router"

import { Item } from "@/client"

import { format_datetime, join } from "@/util"

import classes from "./article.module.css"
import { LikeButton, DislikeButton } from "./like_button"
import MagicButton from "./magic_button"

export default function WallArticle({
  item,
  original,
}: {
  item: Item,
  original?: Item,
}) {
  const [liked, setLiked] = useState(item.like ?? 0);
  const [highlight, setHighlight] = useState(false);

  const is_duplicate = (original !== undefined);
  const [collapsed, setCollapsed] = useState(is_duplicate);
  const card_body_ref = useRef<HTMLDivElement>(null);

  const [title, setTitle] = useState(item.title);
  const [summary, setSummary] = useState(item.summary);

  async function handleCollapse() {
    const card_body = new Collapse(card_body_ref.current!);
    card_body.toggle();
    setCollapsed(!collapsed);
  }

  useEffect(() => {
    const card_body_element = card_body_ref.current!
    const popoverTriggerList = card_body_element.querySelectorAll('[data-bs-toggle="popover"]');
    Array.from(popoverTriggerList).map(popoverTriggerEl =>
      new Popover(popoverTriggerEl, {trigger: "hover"})
    );
  });

  useEffect(() => {
    setCollapsed(is_duplicate);
  }, [original]);

  return (
<div id={ `article-${item.id}` } className="card">
  <div className="card-header" style={ {display: "flex"} }>
    { is_duplicate &&
    <span>
      Duplicate of
      &nbsp;
      <a
        href={ `#article-${original.id}` }
        dangerouslySetInnerHTML={ {__html: `${DOMPurify.sanitize(original.title)} (${original.feed.title})`} }
      />
    </span> }

    <button
      onClick={ handleCollapse }
      style={ {
        backgroundColor: "transparent",
        borderWidth: 0,
        marginLeft: "auto"
      } }
    >
      <i className={ `bi-chevron-${collapsed ? "down" : "up"}` }/>
    </button>
  </div>

  <div
    className={ collapsed ? "card-body collapse" : "card-body collapse show" }
    ref={ card_body_ref }
  >
    <WallArticleTitle item={ item } title={ title }/>
    <WallArticleSubtitle item={ item }/>

    <div
      className={ `card-text ${classes["card-text"]}` }
      dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(summary ?? "")} }
    />
  </div>

  <div className="card-footer">
    <div className="btn-group">
      <LikeButton item={item} liked={liked} setLiked={setLiked}/>
      <DislikeButton item={item} liked={liked} setLiked={setLiked}/>
      <MagicButton
        item={item}
        highlight={highlight}
        setHighlight={setHighlight}
        setTitle={setTitle}
        setSummary={setSummary}
      />
    </div>
  </div>
</div>
  );
}

function WallArticleTitle({
  item,
  title,
}: {
  item: Item,
  title?: string,
}) {
  const link_wo_search_parameters = new URL(item.link);
  link_wo_search_parameters.search = "";

  return (
<h5 className="card-title">
  <a
    href={ `https://archive.is/newest/${link_wo_search_parameters}` }
    target="_blank"
  >
  <i className="bi-box-arrow-up-right"/>
  </a>
  &nbsp;
  <a
    href={ item.link }
    target="_blank"
    dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(title ?? item.title)} }
  />
</h5>
  );
}

function WallArticleSubtitle({
  item,
}: {
  item: Item,
}) {
  const fields: {k: string, v: ReactNode}[] = [
    {k: "Source", v: <Link to={ `/feed/${item.feed.id}/` }>{ item.feed.title }</Link>},
    {k: "Published", v: format_datetime(new Date(item.published))},
    {k: "Tags", v: join(
      item.feed.tags.map(tag_it =>
        <Link to={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</Link>
      ),
      ", ",
    )},
  ];

  if (item.magic) {
    fields.push({k: "Score", v: item.magic.toFixed(2)});
  }

  if (item.surprise) {
    fields.push({k: "Entropy", v: item.surprise.toFixed(2)});
  }

  return (
<h6 className="card-subtitle">
  {
    join(
      fields.map(field_it =>
        <Fragment key={field_it.k}>{field_it.k}: {field_it.v}.</Fragment>
      ),
      "\n",
    )
  }
</h6>
  );
}
