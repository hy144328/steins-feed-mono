import Image from "next/image"
import Link from "next/link"

import { doLanguagesFeedsLangaugesGet, doTagsFeedsTagsGet } from "./actions"
import { LogoutButton } from "./components"

export default async function Navigation({
  now,
}: {
  now: Date,
}) {
  return (
<>
<TopNav now={ now }/>
<SideNav/>
</>
  );
}

async function TopNav({
  now,
}: {
  now: Date,
}) {
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
<li className="nav-item"><Link className="nav-link active" href="/">Home</Link></li>
<li className="nav-item"><a className="nav-link disabled">Settings</a></li>
<li className="nav-item"><a className="nav-link disabled">Statistics</a></li>
</ul>
<ul className="nav">
<li className="nav-item">
<div className="btn-group">
<a className="btn btn-primary" href={ `/?now=${encodeURIComponent(tomorrow.toISOString())}` }><i className="bi-rewind-fill"/></a>
<button className="btn btn-primary" disabled><i className="bi-caret-up-fill"/></button>
<button className="btn btn-primary" disabled><i className="bi-caret-down-fill"/></button>
<a className="btn btn-primary" href={ `/?now=${encodeURIComponent(yesterday.toISOString())}` }><i className="bi-fast-forward-fill"/></a>
</div>
</li>
</ul>
<ul className="nav">
<li className="nav-item">
<LogoutButton/>
</li>
<li className="nav-item">
<button className="btn btn-primary" data-bs-toggle="offcanvas" data-bs-target="#sidenav-offcanvas"><i className="bi-list"/></button>
</li>
</ul>
</div>
</nav>
  );
}

async function SideNav() {
  const languages = doLanguagesFeedsLangaugesGet();
  const tags = doTagsFeedsTagsGet();

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
    <div className="row">
    <div className="col-1">
    <input type="checkbox"/>
    </div>
    <div className="col">
    <label>English</label>
    </div>
    </div>
    <div className="row">
    <div className="col-1">
    <input type="checkbox"/>
    </div>
    <div className="col">
    <label>German</label>
    </div>
    </div>
    <div className="row">
    <div className="col-1">
    <input type="checkbox"/>
    </div>
    <div className="col">
    <label>Swedish</label>
    </div>
    </div>
    </fieldset>
    <fieldset style={ {all: "revert"} }>
    <legend style={ {all: "revert"} }>Tags</legend>
    <div className="row">
    <div className="col-1">
    <input type="checkbox"/>
    </div>
    <div className="col">
    <label>news</label>
    </div>
    </div>
    <div className="row">
    <div className="col-1">
    <input type="checkbox"/>
    </div>
    <div className="col">
    <label>magazines</label>
    </div>
    </div>
    </fieldset>
    </form>
  </div>
</div>
  );
}

function SideNavCheckbox(label: string) {
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
