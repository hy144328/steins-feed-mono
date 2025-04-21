import { Link, NavLink, useNavigate } from "react-router"

import { logout } from "@/auth"

import sf from "./apple-touch-icon.png"
import { NavigationSearchParams, toURLSearchParams } from "./util"

export default function TopNav(
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
    <NavLink to="/" className="navbar-brand">
      <img
        src={ sf }
        height={ 30 }
        width={ 30 }
        alt="Stein's Feed logo"
        className="d-inline-block align-text-top"
      />
      &ensp;
      <span className="d-none d-sm-inline-block">Stein&apos;s Feed</span>
    </NavLink>

    <ul className="nav nav-underline">
      <li className="nav-item">
        <NavLink
          className="nav-link active"
          to={ contentServed ? `/?${toURLSearchParams({now, languages, tags, wall_mode}).toString()}` : "/" }
        >
          Home
        </NavLink>
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
  <Link
    className={ ["btn", "btn-primary"].concat(contentServed ? [] : ["disabled"]).join(" ") }
    to={ contentServed ? `/?${toURLSearchParams({now: tomorrow, languages, tags, wall_mode}).toString()}` : "/" }
  >
    <i className="bi-rewind-fill"/>
  </Link>

  <button className="btn btn-primary" disabled={ true }>
    <i className="bi-caret-up-fill"/>
  </button>

  <button className="btn btn-primary" disabled={ true }>
    <i className="bi-caret-down-fill"/>
  </button>

  <Link
    className={ ["btn", "btn-primary"].concat(contentServed ? [] : ["disabled"]).join(" ") }
    to={ contentServed ? `/?${toURLSearchParams({now: yesterday, languages, tags, wall_mode}).toString()}` : "/" }
  >
    <i className="bi-fast-forward-fill"/>
  </Link>
</div>
  )
}

function LogoutButton() {
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <button className="btn btn-danger">
    <i className="bi-power" onClick={ handleLogout }/>
    </button>
  );
}
