"use client"

import { useState } from "react"
import Button from "react-bootstrap/Button"
import Container from "react-bootstrap/Container"
import Nav from "react-bootstrap/Nav"
import Navbar from "react-bootstrap/Navbar"
import NavbarBrand from "react-bootstrap/NavbarBrand"
import NavItem from "react-bootstrap/NavItem"
import NavLink from "react-bootstrap/NavLink"
import Offcanvas from "react-bootstrap/Offcanvas"


export default function Navigation() {
  const [show, setShow] = useState(false);

  return (
<>
<TopNav setShow={ setShow }/>
<SideNav show={ show } setShow={ setShow }/>
</>
  );
}

function TopNav({
  setShow,
}: {
  setShow: (value: boolean) => void,
}) {
  return (
<Navbar data-bs-theme="dark" bg="dark" sticky="top">
<Container>
<NavbarBrand>Stein&apos;s Feed</NavbarBrand>
<Nav>
<NavItem><NavLink>Bar</NavLink></NavItem>
<NavItem><NavLink>Baz</NavLink></NavItem>
<NavItem><Button><i className="bi-list" onClick={ () => setShow(true) }/></Button></NavItem>
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
