import { Collapse, Popover } from "bootstrap"
import DOMPurify from "dompurify"
import { Fragment, ReactNode } from "react"
import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router"

import {
  Item,
  LikeStatus,
} from "@/client"
import {
  analyzeSummaryItemsAnalyzeSummaryGet,
  analyzeTitleItemsAnalyzeTitleGet,
  likeItemsLikePut,
} from "@/client"

import { authenticate } from "@/auth"
import { wrap_words } from "@/parse"
import { format_datetime, join } from "@/util"

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
    className={ is_duplicate ? "card-body collapse" : "card-body collapse show" }
    ref={ card_body_ref }
  >
    <WallArticleTitle item={ item } title={ title }/>
    <WallArticleSubtitle item={ item }/>

    <div
      className="card-text"
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
  return (
<h5 className="card-title">
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
    {k: "Source", v: <a href={ `/feed/${item.feed.id}/` }>{ item.feed.title }</a>},
    {k: "Published", v: format_datetime(new Date(item.published))},
    {k: "Tags", v: join(
      item.feed.tags.map(tag_it =>
        <a href={ `/tag?tag=${ tag_it.id }` } key={ tag_it.id }>{ tag_it.name }</a>
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

function LikeButton({
  item,
  liked,
  setLiked,
}: {
  item: Item,
  liked: LikeStatus,
  setLiked: (value: LikeStatus) => void,
}) {
  const navigate = useNavigate();

  async function handleLiked() {
    const score = (liked === 1) ? 0 : 1;

    try {
      await putLike(item.id, score);
    } catch(e) {
      console.log(e);
      navigate(0);
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
  const navigate = useNavigate();

  async function handleDisliked() {
    const score = (liked === -1) ? 0 : -1;

    try {
      await putLike(item.id, score);
    } catch(e) {
      console.log(e);
      navigate(0);
    }

    setLiked(score);
  }

  return (
<button className={ `btn btn-outline-${(liked === -1)?"primary":"secondary"}` } onClick={ handleDisliked }>
<i className="bi-hand-thumbs-down-fill"/>
</button>
  );
}

async function putLike(item_id: number, score: LikeStatus) {
  await authenticate();

  const resp = await likeItemsLikePut({
    "query": {
      "item_id": item_id,
      "score": score,
    },
  });

  if (resp.error) {
    throw resp.error;
  }
}

function MagicButton({
  item,
  highlight,
  setHighlight,
  setTitle,
  setSummary,
}: {
  item: Item,
  highlight: boolean,
  setHighlight: (value: boolean) => void,
  setTitle: (value: string) => void,
  setSummary: (value: string | null) => void,
}) {
  function markWord(word: string, bible: Record<string, number>): HTMLElement {
    const res = document.createElement("mark");

    res.textContent = word;
    res.setAttribute("data-bs-toggle", "popover");
    res.setAttribute("data-bs-title", word);
    res.setAttribute("data-bs-content", bible[word].toFixed(2));

    return res;
  }

  async function handleHighlight() {
    if (highlight) {
      setTitle(item.title);
      setSummary(item.summary);
    } else if (item.summary) {
      analyzeTitle(item.id).then(bible => {
        const title = wrap_words(
          item.title,
          Object.entries(bible).filter(([_, v]) =>
            Math.abs(v) >= 0.5
          ).map(([k, _]) =>
            k
          ),
          frag => markWord(frag, bible),
        );
        setTitle(title);
      });

      analyzeSummary(item.id).then(bible => {
        const summary = wrap_words(
          item.summary!,
          Object.entries(bible).filter(([_, v]) =>
            Math.abs(v) >= 0.5
          ).map(([k, _]) =>
            k
          ),
          frag => markWord(frag, bible),
        );
        setSummary(summary);
      });
    }

    setHighlight(!highlight);
  }

  return (
<button className={ `btn btn-outline-${highlight?"primary":"secondary"}` } onClick={ handleHighlight }>
<i className="bi-lightbulb-fill"/>
</button>
  );
};

async function analyzeTitle(
  item_id: number,
): Promise<Record<string, number>> {
  await authenticate();

  const resp = await analyzeTitleItemsAnalyzeTitleGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

async function analyzeSummary(
  item_id: number,
): Promise<Record<string, number>> {
  await authenticate();

  const resp = await analyzeSummaryItemsAnalyzeSummaryGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
