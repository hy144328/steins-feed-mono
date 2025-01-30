"use client"

import { Collapse } from "bootstrap"
import DOMPurify from "isomorphic-dompurify"
import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Fragment, ReactNode, RefObject } from "react"
import { useRef, useState } from "react"

import { Item, Language, LikeStatus, Tag, WallMode } from "@client"
import { format_datetime, join } from "@util"

import { doAnalyzeSummaryGet, doLikeItemsLikePut } from "./actions"
import { logout } from "./auth"
import { NavigationSearchParams, toURLSearchParams } from "./util"

import styles from "./components.module.css"

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

  const [summary, setSummary] = useState(item.summary);
  const summary_ref = useRef<HTMLDivElement>(null);

  async function handleCollapse() {
    const card_body = new Collapse(card_body_ref.current!);
    card_body.toggle();
    setCollapsed(!collapsed);
  }

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
    <WallArticleTitle item={ item }/>
    <WallArticleSubtitle item={ item }/>

    <div
      className={ `card-text ${styles["card-text"]}` }
      ref={ summary_ref }
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
        summaryRef={summary_ref}
        setSummary={setSummary}
      />
    </div>
  </div>
</div>
  );
}

function WallArticleTitle({
  item,
}: {
  item: Item,
}) {
  return (
<h5 className="card-title">
  <a
    href={ item.link }
    target="_blank"
    dangerouslySetInnerHTML={ {__html: DOMPurify.sanitize(item.title)} }
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
    {k: "Source", v: <a href={ `/feed?feed=${item.feed.id}` }>{ item.feed.title }</a>},
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
  item,
  highlight,
  setHighlight,
  summaryRef,
  setSummary,
}: {
  item: Item,
  highlight: boolean,
  setHighlight: (value: boolean) => void,
  summaryRef: RefObject<HTMLElement | null>,
  setSummary: (value: string | null) => void,
}) {
  async function handleHighlight() {
    if (highlight) {
      setSummary(item.summary);
    } else if (item.summary) {
      let summary = item.summary;
      const bible = await doAnalyzeSummaryGet(item);

      for (const [k, v] of Object.entries(bible)) {
        if (Math.abs(v) >= 0.5) {
          summary = summary.replace(new RegExp(`\\b${k}\\b`, "gi"), "<em>$&</em>");
        }
      }

      setSummary(summary);
    }

    setHighlight(!highlight);
  }

  return (
<button className={ `btn btn-outline-${highlight?"primary":"secondary"}` } onClick={ handleHighlight }>
<i className="bi-lightbulb-fill"/>
</button>
  );
};

export function TopNav(
{
  now,
  languages,
  tags,
  wall_mode,
  contentServed = false,
}: NavigationSearchParams & {
  contentServed?: boolean,
}) {
  return (
<nav className="navbar bg-dark sticky-top" data-bs-theme="dark">
  <div className="container">
    <Link href="/" className="navbar-brand">
      <Image
        src="/apple-touch-icon.png"
        height={ 30 }
        width={ 30 }
        alt="Stein's Feed logo"
        className="d-inline-block align-text-top"
      />
      &ensp;
      <span className="d-none d-sm-inline-block">Stein&apos;s Feed</span>
    </Link>

    <ul className="nav nav-underline">
      <li className="nav-item">
        <Link
          className="nav-link active"
          href={ contentServed ? `/?${toURLSearchParams({now, languages, tags, wall_mode}).toString()}` : "/" }
        >
          Home
        </Link>
      </li>

      <li className="nav-item">
        <a className="nav-link disabled">
          Settings
        </a>
      </li>

      <li className="nav-item">
        <a className="nav-link disabled">
          Statistics
        </a>
      </li>
    </ul>

    <ul className="nav">
      <li className="nav-item">
        <NavigationPad
          now={ now }
          languages={ languages }
          tags={ tags }
          wall_mode={ wall_mode }
          contentServed={ contentServed }
        />
      </li>
    </ul>

    <ul className="nav">
      <li className="nav-item">
        <LogoutButton/>
      </li>

      <li className="nav-item">
        <button
          className="btn btn-primary"
          data-bs-toggle="offcanvas"
          data-bs-target="#sidenav-offcanvas"
          disabled={ !contentServed }
        >
          <i className="bi-list"/>
        </button>
      </li>
    </ul>
  </div>
</nav>
  );
}

function NavigationPad(
{
  now,
  languages,
  tags,
  wall_mode,
  contentServed = true,
}: NavigationSearchParams & {
  contentServed?: boolean,
}) {
  const yesterday = new Date(now);
  yesterday.setUTCDate(now.getUTCDate() - 1);

  const tomorrow = new Date(now);
  tomorrow.setUTCDate(now.getUTCDate() + 1);

  return (
<div className="btn-group">
  <a
    className={ ["btn", "btn-primary"].concat(contentServed ? [] : ["disabled"]).join(" ") }
    href={ contentServed ? `/?${toURLSearchParams({now: tomorrow, languages, tags, wall_mode}).toString()}` : undefined }
  >
    <i className="bi-rewind-fill"/>
  </a>

  <button className="btn btn-primary" disabled={ true }>
    <i className="bi-caret-up-fill"/>
  </button>

  <button className="btn btn-primary" disabled={ true }>
    <i className="bi-caret-down-fill"/>
  </button>

  <a
    className={ ["btn", "btn-primary"].concat(contentServed ? [] : ["disabled"]).join(" ") }
    href={ contentServed ? `/?${toURLSearchParams({now: yesterday, languages, tags, wall_mode}).toString()}` : undefined }
  >
    <i className="bi-fast-forward-fill"/>
  </a>
</div>
  )
}

export function SideNav({
  now,
  languages,
  tags,
  wall_mode,
  all_languages,
  all_tags,
}: NavigationSearchParams & {
  all_languages: Language[],
  all_tags: Tag[],
}) {
  const router = useRouter();

  const re_lang = /lang-([A-Za-z]+)/;
  const re_tag = /tag-([0-9]+)/;

  const languages_check = all_languages.map(lang_it =>
    <SideNavCheckbox
      name={ `lang-${lang_it}` }
      label={ lang_it }
      key={ `lang-${lang_it.toLowerCase()}` }
      checked={ languages.includes(lang_it) }
    />
  );
  const tags_check = all_tags.map(tag_it =>
    <SideNavCheckbox
      name={ `tag-${tag_it.id}` }
      label={ tag_it.name }
      key={ `tag-${tag_it.id}` }
      checked={ tags.includes(tag_it.id) }
    />
  );
  const wall_radio = [
    "Classic",
    "Magic",
    "Random",
    "Surprise",
  ].map(wall_it =>
    <SideNavRadio
      name="wall_mode"
      value={ wall_it }
      label={ wall_it }
      key={ `wall-${wall_it}` }
      checked={ wall_it === wall_mode }
    />
  )

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);

    const now = new Date(data.get("now") as string);
    const languages = data.entries().filter(([k, _]) =>
      re_lang.test(k)
    ).filter(([_, v]) =>
      v === "on"
    ).map(([k, _]) =>
      re_lang.exec(k)![1] as Language
    ).toArray();
    const tags = data.entries().filter(([k, _]) =>
      re_tag.test(k)
    ).filter(([_, v]) =>
      v === "on"
    ).map(([k, _]) =>
      parseInt(re_tag.exec(k)![1])
    ).toArray();
    const wall_mode = data.get("wall_mode") as WallMode;

    router.push(`/?${toURLSearchParams({now, languages, tags, wall_mode})}`);
  }

  return (
<div
  id="sidenav-offcanvas"
  className="offcanvas offcanvas-end"
  data-bs-backdrop="static"
  data-bs-scroll="true"
>
  <div className="offcanvas-header">
    <h4 className="offcanvas-title">Filters</h4>
    <button className="btn-close" data-bs-dismiss="offcanvas"/>
  </div>

  <div className="offcanvas-body">
    <form onSubmit={ handleSubmit }>
      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Languages</legend>
        { languages_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Tags</legend>
        { tags_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Wall</legend>
        { wall_radio }
      </fieldset>

      <fieldset className="mt-3" style={ {all: "revert"} }>
        <input type="hidden" name="now" value={ now.toISOString() }/>

        <div className="btn-group">
          <input type="submit" className="btn btn-primary" data-bs-dismiss="offcanvas"/>
          <input type="reset" className="btn btn-secondary"/>
        </div>
      </fieldset>
    </form>
  </div>
</div>
  );
}

function SideNavCheckbox({
  name,
  label,
  checked = false,
}: {
  name: string,
  label: string,
  checked?: boolean,
}) {
  return (
<div className="form-check">
  <label className="form-check-label">{ label }</label>
  <input
    type="checkbox"
    name={ name }
    defaultChecked={ checked }
    className="form-check-input"
  />
</div>
  );
}

function SideNavRadio({
  name,
  value,
  label,
  checked = false,
}: {
  name: string,
  value: string,
  label: string,
  checked?: boolean,
}) {
  return (
<div className="form-check">
  <label className="form-check-label">{ label }</label>
  <input
    type="radio"
    name={ name }
    value={ value }
    defaultChecked={ checked }
    className="form-check-input"
  />
</div>
  );
}

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
