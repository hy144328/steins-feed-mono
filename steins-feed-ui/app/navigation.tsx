"use client"

import { useRouter } from "next/navigation"

import { logout } from "./auth"

export default function Navigation({
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

function TopNav({
  now,
}: {
  now: Date,
}) {
  const router = useRouter();

  const yesterday = new Date(now);
  yesterday.setUTCDate(now.getUTCDate() - 1);

  const tomorrow = new Date(now);
  tomorrow.setUTCDate(now.getUTCDate() + 1);

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
<nav className="navbar bg-dark sticky-top" data-bs-theme="dark">
<div className="container">
<a className="navbar-brand">
<img
  src="/apple-touch-icon.png"
  className="d-inline-block align-text-top"
  style={ {height: "1.5em", width: "1.5em"} }
  alt="Stein's Feed logo"
/>
&nbsp;
Stein&apos;s Feed
</a>
<ul className="nav nav-underline">
<li className="nav-item"><a className="nav-link active" href="/">Home</a></li>
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
<button className="btn btn-danger"><i className="bi-power" onClick={ handleLogout }/></button>
</li>
<li className="nav-item">
<button className="btn btn-primary" data-bs-toggle="offcanvas" data-bs-target="#sidenav-offcanvas"><i className="bi-list"/></button>
</li>
</ul>
</div>
</nav>
  );
}

function SideNav() {
  return (
<div id="sidenav-offcanvas" className="offcanvas offcanvas-end" data-bs-scroll="true">
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
    <label htmlFor="foo">English</label>
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
