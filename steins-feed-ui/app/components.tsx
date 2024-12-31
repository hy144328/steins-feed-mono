"use client"

import { Collapse } from "bootstrap"
import { useRouter } from "next/navigation"
import DOMPurify from "isomorphic-dompurify"
import { useRef, useState } from "react"

import { Item, LikeStatus } from "@client"
import { format_datetime, join } from "@util"

import { doLikeItemsLikePut } from "./actions"
import { logout } from "./auth"

export default function WallArticle({
  item,
}: {
  item: Item,
}) {
  const [liked, setLiked] = useState(item.like ?? 0);
  const [highlight, setHighlight] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  const card_body_ref = useRef<HTMLDivElement>(null);

  async function handleCollapse() {
    const card_body = new Collapse(card_body_ref.current!);
    card_body.toggle();
    setCollapsed(!collapsed);
  }

  return (
<div className="card">
  <div className="card-header">
  <button
    onClick={ handleCollapse }
    style={ {
      backgroundColor: "transparent",
      borderWidth: 0,
      display: "flex",
      justifyContent: "end",
      width: "100%",
    } }
  >
  <i className={ `bi-chevron-${collapsed ? "down" : "up"}` }/>
  </button>
  </div>

  <div className="card-body collapse show" ref={ card_body_ref }>
    <h5 className="card-title">
      <a href={ item.link } target="_blank">{ item.title }</a>
    </h5>

    <h6 className="card-subtitle">
      Source: <a href={ `/feed?feed=${item.feed.id}` }>{ item.feed.title }</a>.
      Published: { format_datetime(new Date(item.published)) }.
      Tags: { join(
        item.feed.tags.map(tag_it =>
          <a href={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</a>
        ),
        ",",
      ) }.
      Score: { (item.magic ?? 0).toFixed(2) }.
    </h6>

    <div
      className="card-text"
      dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(item.summary ?? "")} }
    />
  </div>

  <div className="card-footer">
    <div className="btn-group">
      <LikeButton item={item} liked={liked} setLiked={setLiked}/>
      <DislikeButton item={item} liked={liked} setLiked={setLiked}/>
      <MagicButton /*item={item}*/ highlight={highlight} setHighlight={setHighlight}/>
    </div>
  </div>
</div>
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
<button className={ `btn btn-outline-${(liked === 1)?"primary":"secondary"}` } onClick={ handleLiked }>
<i className="bi-hand-thumbs-up-fill"/>
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
<button className={ `btn btn-outline-${(liked === -1)?"primary":"secondary"}` } onClick={ handleDisliked }>
<i className="bi-hand-thumbs-down-fill"/>
</button>
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
<button className={ `btn btn-outline-${highlight?"primary":"secondary"}` } onClick={ () => setHighlight(!highlight) } disabled>
<i className="bi-lightbulb-fill"/>
</button>
  );
};

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <button className="btn btn-danger">
    <i className="bi-power" onClick={ handleLogout }/>
    </button>
  );
}
