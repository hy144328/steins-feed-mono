"use client"

import { useRouter } from "next/navigation"
import { useEffect, useRef } from "react"

import { doLoginTokenPost } from "./actions"

export default function LoginModal({
  callback,
}: {
  callback: string | (() => void),
}) {
  const router = useRouter();
  const modal_ref = useRef<HTMLDivElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);
    const username = data.get("username") as string;
    const password = data.get("password") as string;

    try {
      await doLoginTokenPost(username, password);
    } catch(exc) {
      alert("Incorrect username or password.");
      throw exc;
    }

    if (typeof callback === "string") {
      router.push(callback);
    } else {
      callback();
    }
  }

  useEffect(() => {
    let modal;

    import("bootstrap").then(({Modal}) => {
      modal = new Modal(modal_ref.current!);
      modal.show();
    });

    return () => {
      modal.hide();
    };
  });

  return (
<div className="modal fade" data-bs-backdrop="static" ref={ modal_ref }>
  <div className="modal-dialog">
    <div className="modal-content">
      <div className="modal-header">
        <h4 className="modal-title">Log in</h4>
      </div>

      <div className="modal-body">
        <form id="login" onSubmit={ handleSubmit }>
          <div className="form-floating mt-3 mb-3">
            <input
              name="username"
              required
              placeholder="Enter name."
              className="form-control"
            />
            <label>Username</label>
          </div>

          <div className="form-floating mt-3 mb-3">
            <input
              name="password"
              type="password"
              required
              placeholder="Enter password."
              className="form-control"
            />
            <label>Password</label>
          </div>
        </form>
      </div>

      <div className="modal-footer">
        <input form="login" className="btn btn-primary" type="submit"/>
      </div>
    </div>
  </div>
</div>
  );
}
