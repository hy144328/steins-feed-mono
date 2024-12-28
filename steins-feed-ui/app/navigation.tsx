"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import Offcanvas from "react-bootstrap/Offcanvas"

import { logout } from "./auth"

export default function Navigation({
  now,
}: {
  now: Date,
}) {
  const [show, setShow] = useState(false);

  return (
<>
<TopNav now={ now } setShow={ setShow }/>
<SideNav show={ show } setShow={ setShow }/>
</>
  );
}

function TopNav({
  now,
  setShow,
}: {
  now: Date,
  setShow: (value: boolean) => void,
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
<button className="btn btn-primary"><i className="bi-list" onClick={ () => setShow(true) }/></button>
</li>
</ul>
</div>
</nav>
  );
}

function SideNav({
  show,
  setShow,
}: {
  show: boolean,
  setShow: (value: boolean) => void,
}) {
  return (
<Offcanvas show={show} onHide={ () => setShow(false) } placement="end" scroll={ true }>
  <Offcanvas.Header closeButton>
    <Offcanvas.Title>Filters</Offcanvas.Title>
  </Offcanvas.Header>
  <Offcanvas.Body>
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
  </Offcanvas.Body>
</Offcanvas>
  );
}
