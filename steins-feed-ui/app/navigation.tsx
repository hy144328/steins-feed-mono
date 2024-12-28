"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import Button from "react-bootstrap/Button"
import ButtonGroup from "react-bootstrap/ButtonGroup"
import Container from "react-bootstrap/Container"
import Nav from "react-bootstrap/Nav"
import Navbar from "react-bootstrap/Navbar"
import NavbarBrand from "react-bootstrap/NavbarBrand"
import NavItem from "react-bootstrap/NavItem"
import NavLink from "react-bootstrap/NavLink"
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
<Navbar data-bs-theme="dark" bg="dark" sticky="top">
<Container>
<NavbarBrand>
<img
  src="/apple-touch-icon.png"
  style={ {display: "inline-block", height: "1.5em", verticalAlign: "top", width: "1.5em"} }
  alt="Stein's Feed logo"
/>
&nbsp;
Stein&apos;s Feed
</NavbarBrand>
<Nav variant="underline">
<NavItem><NavLink href="/" active>Home</NavLink></NavItem>
<NavItem><NavLink disabled>Settings</NavLink></NavItem>
<NavItem><NavLink disabled>Statistics</NavLink></NavItem>
</Nav>
<Nav>
<NavItem>
<ButtonGroup>
<Button href={ `/?now=${encodeURIComponent(tomorrow.toISOString())}` }><i className="bi-rewind-fill"/></Button>
<Button disabled><i className="bi-caret-up-fill"/></Button>
<Button disabled><i className="bi-caret-down-fill"/></Button>
<Button href={ `/?now=${encodeURIComponent(yesterday.toISOString())}` }><i className="bi-fast-forward-fill"/></Button>
</ButtonGroup>
</NavItem>
</Nav>
<Nav>
<NavItem>
<ButtonGroup>
<Button variant="danger"><i className="bi-power" onClick={ handleLogout }/></Button>
<Button><i className="bi-list" onClick={ () => setShow(true) }/></Button>
</ButtonGroup>
</NavItem>
</Nav>
</Container>
</Navbar>
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
    <Offcanvas.Title>Offcanvas</Offcanvas.Title>
  </Offcanvas.Header>
  <Offcanvas.Body>
    Some text as placeholder. In real life you can have the elements you
    have chosen. Like, text, images, lists, etc.
  </Offcanvas.Body>
</Offcanvas>
  );
}
