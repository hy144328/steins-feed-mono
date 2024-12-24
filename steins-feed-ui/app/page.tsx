"use client"

import { useState } from "react"

export default function Page() {
  const items: Item[] = [
    {
      id: 0,
      title: "Item title",
      link: "https://www.link.com",
      feed_id: 0,
      published: new Date(0),
      summary: "Bla bla bla.",
      feed: {
        id: 0,
        title: "Feed title",
        tags: [
          {
            id: 0,
            name: "news",
            user_id: 0,
          },
          {
            id: 1,
            name: "magazines",
            user_id: 0,
          },
        ],
      },
      like: {
        item_id: 0,
        user_id: 0,
        score: LikeStatus.UP,
      },
      magic: {
        item_id: 0,
        user_id: 0,
        score: 0,
      },
    },
    {
      id: 1,
      title: "Item title",
      link: "https://www.link.com",
      feed_id: 0,
      published: new Date(0),
      summary: "Bla bla bla.",
      feed: {
        id: 0,
        title: "Feed title",
        tags: [
          {
            id: 0,
            name: "news",
            user_id: 0,
          },
          {
            id: 1,
            name: "magazines",
            user_id: 0,
          },
        ],
      },
      like: {
        item_id: 1,
        user_id: 0,
        score: LikeStatus.DOWN,
      },
      magic: {
        item_id: 1,
        user_id: 0,
        score: 0,
      },
    },
    {
      id: 2,
      title: "Item title",
      link: "https://www.link.com",
      feed_id: 0,
      published: new Date(0),
      summary: "Bla bla bla.",
      feed: {
        id: 0,
        title: "Feed title",
        tags: [
          {
            id: 0,
            name: "news",
            user_id: 0,
          },
          {
            id: 1,
            name: "magazines",
            user_id: 0,
          },
        ],
      },
      like: {
        item_id: 2,
        user_id: 0,
        score: LikeStatus.MEH,
      },
      magic: {
        item_id: 2,
        user_id: 0,
        score: 0,
      },
    },
  ];

  const articles_hr: React.ReactNode[] = [];
  for (const item_it of items) {
    articles_hr.push(<WallArticle item={item_it} wall_mode={WallMode.MAGIC} key={ `article_${item_it.id}` }/>)
    articles_hr.push(<hr className="article-hr" key={`article_hr_${item_it.id}`}/>)
  }

  return <>{articles_hr}</>
}

interface Item {
  id: number
  title: string
  link: string
  feed_id: number
  published: Date
  summary: string
  feed: Feed
  like: Like
  magic: Magic
}

interface Feed {
  id: number
  title: string
  tags: Tag[]
}

interface Tag {
  id: number
  name: string
  user_id: number
}

interface Like {
  item_id: number
  user_id: number
  score: LikeStatus
}

interface Magic {
  item_id: number
  user_id: number
  score: number
}

enum WallMode {
  MAGIC,
  SURPRISE,
}

enum LikeStatus {
  DOWN = -1,
  MEH = 0,
  UP = 1,
}

function WallArticle({
  item,
  wall_mode,
}: {
  item: Item,
  wall_mode: WallMode,
}) {
  const [liked, setLiked] = useState(item.like.score);
  const [highlight, setHighlight] = useState(false);

  const tags = item.feed.tags.map(tag_it =>
<a href={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</a>
  );

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

Published: { item.published.toISOString() }.

Tags: { tags.map((value, index) => [(index > 0) && ", ", value]) }.

Score: { item.magic.score.toFixed(2) }.
</p>

<div id={ `summary_${item.id}` }>
{ item.summary }
</div>

<p>
<LikeButton item={item} liked={liked} setLiked={setLiked}/>
<DislikeButton item={item} liked={liked} setLiked={setLiked}/>
<MagicButton item={item} highlight={highlight} setHighlight={setHighlight}/>
</p>
</article>
  )
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
  function handleLike() {
    if (liked == LikeStatus.UP) {
      setLiked(LikeStatus.MEH);
    } else {
      setLiked(LikeStatus.UP);
    }
  }

  return (
<button type="button" onClick={ handleLike }>
<span id={ `like_${ item.id }` } className={ (liked == LikeStatus.UP) ? "liked" : "like" }>
<i className="material-icons">thumb_up</i>
</span>
</button>
  )
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
  function handleDislike() {
    if (liked == LikeStatus.DOWN) {
      setLiked(LikeStatus.MEH);
    } else {
      setLiked(LikeStatus.DOWN);
    }
  }

  return (
<button type="button" onClick={ handleDislike }>
<span id={ `dislike_${ item.id }` } className={ (liked == LikeStatus.DOWN) ? "disliked" : "dislike" }>
<i className="material-icons">thumb_down</i>
</span>
</button>
  )
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
  function handleHighlight() {
    setHighlight(!highlight);
  }

  return (
<button type="button" onClick={ handleHighlight }>
<span id={ `highlight_${ item.id }` } className={ highlight ? "highlit" : "highlight" }>
<i className="material-icons">lightbulb_outline</i>
</span>
</button>
  )
}
