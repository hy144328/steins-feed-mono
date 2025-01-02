import Image from "next/image"
import Link from "next/link"

import { NavigationSearchParams, toURLSearchParams } from "./util"

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
    <form>
      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Languages</legend>
        { languages_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Tags</legend>
        { tags_check }
      </fieldset>

      <fieldset className="mt-3" style={ {all: "revert"} }>
        <input type="hidden" value={ now.toISOString() }/>

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

async function SideNavCheckbox({
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
