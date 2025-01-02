"use client"

import { Collapse } from "bootstrap"
import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import DOMPurify from "isomorphic-dompurify"
import { useRef, useState } from "react"

import { Item, Language, LikeStatus, Tag } from "@client"
import { format_datetime, join } from "@util"

import { doLikeItemsLikePut } from "./actions"
import { logout } from "./auth"
import { NavigationSearchParams, toURLSearchParams } from "./util"

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

export function TopNav(
{
  now,
  languages,
  tags,
}: NavigationSearchParams) {
  const yesterday = new Date(now);
  yesterday.setUTCDate(now.getUTCDate() - 1);

  const tomorrow = new Date(now);
  tomorrow.setUTCDate(now.getUTCDate() + 1);

  return (
<nav className="navbar bg-dark sticky-top" data-bs-theme="dark">
  <div className="container">
    <a className="navbar-brand">
      <Image
        src="/apple-touch-icon.png"
        height={ 30 }
        width={ 30 }
        alt="Stein's Feed logo"
        className="d-inline-block align-text-top"
      />
      &nbsp;
      Stein&apos;s Feed
    </a>

    <ul className="nav nav-underline">
      <li className="nav-item">
        <Link
          className="nav-link active"
          href={ `/?${toURLSearchParams({now, languages, tags}).toString()}` }
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
        <div className="btn-group">
          <a
            className="btn btn-primary"
            href={ `/?${toURLSearchParams({now: tomorrow, languages, tags}).toString()}` }
          >
            <i className="bi-rewind-fill"/>
          </a>

          <button className="btn btn-primary" disabled>
            <i className="bi-caret-up-fill"/>
          </button>

          <button className="btn btn-primary" disabled>
            <i className="bi-caret-down-fill"/>
          </button>

          <a
            className="btn btn-primary"
            href={ `/?${toURLSearchParams({now: yesterday, languages, tags}).toString()}` }
          >
            <i className="bi-fast-forward-fill"/>
          </a>
        </div>
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
        >
          <i className="bi-list"/>
        </button>
      </li>
    </ul>
  </div>
</nav>
  );
}

export function SideNav({
  now,
  languages,
  tags,
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

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);

    const now = new Date(data.get("now") as string);
    const languages = data.entries().filter(([k, v]) =>
      re_lang.test(k)
    ).filter(([k, v]) =>
      v === "on"
    ).map(([k]) =>
      re_lang.exec(k)![1] as Language
    ).toArray();
    const tags = data.entries().filter(([k, v]) =>
      re_tag.test(k)
    ).filter(([k, v]) =>
      v === "on"
    ).map(([k]) =>
      parseInt(re_tag.exec(k)![1])
    ).toArray();

    router.push(`/?${toURLSearchParams({now, languages, tags})}`);
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

      <fieldset className="mt-3" style={ {all: "revert"} }>
        <input type="hidden" name="now" value={ now.toISOString() }/>

        <div className="btn-group">
          <input type="submit" className="btn btn-primary"/>
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
