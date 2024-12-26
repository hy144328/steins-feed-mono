"use client"

import DOMPurify from "isomorphic-dompurify"
import { useState } from "react"

import { Item, LikeStatus } from "@client"
import { format_datetime, join_const } from "@util"

import { doLikeItemsLikePut } from "./actions"
import styles from "./components.module.css"

export default function WallArticle({
  item,
}: {
  item: Item,
}) {
  const [liked, setLiked] = useState(item.like ?? 0);
  const [highlight, setHighlight] = useState(false);

  return (
<article id={ `article_${item.id}` }>
<h2>
<a href={ item.link } target="_blank">
<span id={ `title_${item.id}` }>
{ item.title }
</span>
</a>
</h2>

<p>
Source: <a href={ `/feed?feed=${item.feed.id}` }>{ item.feed.title }</a>.

Published: { format_datetime(new Date(item.published)) }.

Tags: { join_const(
  item.feed.tags.map(tag_it =>
    <a href={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</a>
  ),
  ",",
) }.

Score: { (item.magic ?? 0).toFixed(2) }.
</p>

<div id={ `summary_${item.id}` } dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(item.summary ?? "")} } />

<p>
<LikeButton item={item} liked={liked} setLiked={setLiked}/>
<DislikeButton item={item} liked={liked} setLiked={setLiked}/>
<MagicButton item={item} highlight={highlight} setHighlight={setHighlight}/>
</p>
</article>
  );
}

function LikeButton({
  item,
  liked,
  setLiked,
}: {
  item: Item,
  liked: LikeStatus,
  setLiked: (value: LikeStatus) => void,
}) {
  async function handleLiked() {
    const score = (liked === 1) ? 0 : 1;
    await doLikeItemsLikePut(item, score);
    setLiked(score);
  }

  return (
<button type="button" onClick={ handleLiked }>
<span id={ `like_${ item.id }` } className={ (liked === 1) ? styles.liked : "like" }>
<i className="material-icons">thumb_up</i>
</span>
</button>
  );
}

function DislikeButton({
  item,
  liked,
  setLiked,
}: {
  item: Item,
  liked: LikeStatus,
  setLiked: (value: LikeStatus) => void,
}) {
  async function handleDisliked() {
    const score = (liked === -1) ? 0 : -1;
    await doLikeItemsLikePut(item, score);
    setLiked(score);
  }

  return (
<button type="button" onClick={ handleDisliked }>
<span id={ `dislike_${ item.id }` } className={ (liked === -1) ? styles.disliked : "dislike" }>
<i className="material-icons">thumb_down</i>
</span>
</button>
  );
}

function MagicButton({
  item,
  highlight,
  setHighlight,
}: {
  item: Item,
  highlight: boolean,
  setHighlight: (value: boolean) => void,
}) {
  return (
<button type="button" onClick={ () => setHighlight(!highlight) }>
<span id={ `highlight_${ item.id }` } className={ highlight ? styles.highlit : "highlight" }>
<i className="material-icons">lightbulb_outline</i>
</span>
</button>
  );
};
