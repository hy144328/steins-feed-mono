"use client"

import { useRouter } from "next/navigation"
import DOMPurify from "isomorphic-dompurify"
import { useState } from "react"
import Button from 'react-bootstrap/Button'
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Card from 'react-bootstrap/Card'

import { Item, LikeStatus } from "@client"
import { format_datetime, join } from "@util"

import { doLikeItemsLikePut } from "./actions"

export default function WallArticle({
  item,
}: {
  item: Item,
}) {
  const [liked, setLiked] = useState(item.like ?? 0);
  const [highlight, setHighlight] = useState(false);

  return (
<Card>
<Card.Body>
<Card.Title>
<a href={ item.link } target="_blank">{ item.title }</a>
</Card.Title>

<Card.Subtitle>
Source: <a href={ `/feed?feed=${item.feed.id}` }>{ item.feed.title }</a>.
Published: { format_datetime(new Date(item.published)) }.
Tags: { join(
  item.feed.tags.map(tag_it =>
    <a href={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</a>
  ),
  ",",
) }.
Score: { (item.magic ?? 0).toFixed(2) }.
</Card.Subtitle>

<Card.Text as="div" dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(item.summary ?? "")} }/>
</Card.Body>

<Card.Footer>
<ButtonGroup>
<LikeButton item={item} liked={liked} setLiked={setLiked}/>
<DislikeButton item={item} liked={liked} setLiked={setLiked}/>
<MagicButton /*item={item}*/ highlight={highlight} setHighlight={setHighlight}/>
</ButtonGroup>
</Card.Footer>
</Card>
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
  const router = useRouter();

  async function handleLiked() {
    const score = (liked === 1) ? 0 : 1;

    try {
      await doLikeItemsLikePut(item, score);
    } catch(e) {
      console.log(e);
      router.refresh();
    }

    setLiked(score);
  }

  return (
<Button variant={ (liked === 1) ? "outline-primary" : "outline-secondary" } onClick={ handleLiked }>
<i className="bi-hand-thumbs-up-fill"/>
</Button>
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
  const router = useRouter();

  async function handleDisliked() {
    const score = (liked === -1) ? 0 : -1;

    try {
      await doLikeItemsLikePut(item, score);
    } catch(e) {
      console.log(e);
      router.refresh();
    }

    setLiked(score);
  }

  return (
<Button variant={ (liked === -1) ? "outline-primary" : "outline-secondary" } onClick={ handleDisliked }>
<i className="bi-hand-thumbs-down-fill"/>
</Button>
  );
}

function MagicButton({
  //item,
  highlight,
  setHighlight,
}: {
  //item: Item,
  highlight: boolean,
  setHighlight: (value: boolean) => void,
}) {
  return (
<Button variant={ highlight ? "outline-primary" : "outline-secondary" } onClick={ () => setHighlight(!highlight) } disabled>
<i className="bi-lightbulb-fill"/>
</Button>
  );
};
