import Image from "next/image"
import Link from "next/link"

import { Language } from "@client"

import { doLanguagesFeedsLangaugesGet, doTagsFeedsTagsGet } from "./actions"
import { LogoutButton } from "./components"

export default async function Navigation({
  now,
  languages,
  tags,
}: NavigationSearchParams) {
  return (
<>
<TopNav now={ now } languages={ languages } tags={ tags }/>
<SideNav now={ now } languages={ languages } tags={ tags }/>
</>
  );
}

async function TopNav({
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

async function SideNav({
  now,
  languages,
  tags,
}: NavigationSearchParams) {
  const all_languages = await doLanguagesFeedsLangaugesGet();
  const all_tags = await doTagsFeedsTagsGet();

  const languages_check = all_languages.map(lang_it =>
    <SideNavCheckbox label={ lang_it } key={ `lang-${lang_it.toLowerCase()}` }/>
  );
  const tags_check = all_tags.map(tag_it =>
    <SideNavCheckbox label={ tag_it.name } key={ `tag-${tag_it.id}` }/>
  );

  return (
<div id="sidenav-offcanvas" className="offcanvas offcanvas-end" data-bs-backdrop="static" data-bs-scroll="true">
  <div className="offcanvas-header">
    <h4 className="offcanvas-title">Filters</h4>
    <button className="btn-close" data-bs-dismiss="offcanvas"/>
  </div>

  <div className="offcanvas-body">
    <form>
      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Languages</legend>
        { languages_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Tags</legend>
        { tags_check }
      </fieldset>
    </form>
  </div>
</div>
  );
}

interface NavigationSearchParams {
  now: Date,
  languages: Language[],
  tags: number[],
};

function toURLSearchParams({
  now,
  languages,
  tags,
}: NavigationSearchParams): URLSearchParams {
  const res = new URLSearchParams();

  res.append("now", now.toISOString());
  languages.forEach(lang_it => res.append("languages", lang_it));
  tags.forEach(tag_it => res.append("tags", tag_it.toString()));

  return res;
}

async function SideNavCheckbox({
  label,
}: {
  label: string,
}) {
  return (
<div className="row">
  <div className="col-1">
    <input type="checkbox"/>
  </div>

  <div className="col">
    <label>{ label }</label>
  </div>
</div>
  );
}
