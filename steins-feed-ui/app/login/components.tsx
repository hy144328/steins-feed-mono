"use client"

import { useRouter } from "next/navigation"
import Col from "react-bootstrap/Col"
import Modal from "react-bootstrap/Modal"
import Row from "react-bootstrap/Row"

import { doLoginTokenPost } from "./actions"

export default function LoginModal({
  callback,
  open,
  setOpen,
}: {
  callback: string | (() => void),
  open?: boolean,
  setOpen?: (value: boolean) => void,
}) {
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);
    const username = data.get("username");
    const password = data.get("password");

    if (typeof username === "string" && typeof password === "string") {
      try {
        await doLoginTokenPost(username, password);
      } catch(exc) {
        alert("Incorrect username or password.");
        throw exc;
      }
    } else {
      throw data;
    }

    if (typeof callback === "string") {
      router.push(callback);
    } else {
      callback();
    }
  }

  return (
<Modal show={ open ?? true } onHide={ setOpen ? () => setOpen(false) : undefined }>
<Modal.Header closeButton={ setOpen !== undefined }>
<Modal.Title>Log in</Modal.Title>
</Modal.Header>
<Modal.Body>
<form id="login" onSubmit={ handleSubmit }>
<Row>
<Col xs={ 2 }>
<label className="form-label col-form-label">User</label>
</Col>
<Col>
<input
  name="username"
  required
  placeholder="Enter name."
  className="form-control"
  style={ {"width": "100%"} }
/>
</Col>
</Row>
<Row>
<Col xs={ 2 }>
<label className="form-label col-form-label">Password</label>
</Col>
<Col>
<input
  name="password"
  type="password"
  required
  placeholder="Enter password."
  className="form-control"
  style={ {"width": "100%"} }
/>
</Col>
</Row>
</form>
</Modal.Body>
<Modal.Footer>
<input form="login" className="btn btn-primary" type="submit"/>
</Modal.Footer>
</Modal>
  );
}
