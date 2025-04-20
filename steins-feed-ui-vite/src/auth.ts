/*
import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { client } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL});
*/

export async function logout() {
  /*
  const cookie_store = await cookies();
  cookie_store.delete("api_token");
  */
}

export async function authenticate() {
  /*
  const cookie_store = await cookies();
  const cookie = cookie_store.get("api_token");

  if (!cookie) {
    throw {"detail": "Not authenticated"};
  }

  client.interceptors.request.use(request => {
    request.headers.set("Authorization", `Bearer ${cookie.value}`);
    return request;
  });
  */
}

/*
export async function require_login(pathname: string) {
  redirect(`/login?pathname=${encodeURIComponent(pathname)}`);
}

export async function skip_login_if_unnecessary(pathname: string) {
  const cookie_store = await cookies();
  const cookie = cookie_store.get("api_token");

  if (!cookie) {
    return;
  }

  const payload = decode_jwt(cookie.value);
  if (payload.exp <= new Date()) {
    return;
  }

  redirect(pathname);
}

function decode_jwt(token: string): {sub: string, exp: Date} {
  const payload_enc = token.split(".")[1];
  const payload_dec = Buffer.from(payload_enc, "base64").toString();
  const payload = JSON.parse(payload_dec);

  return {
    sub: payload.sub,
    exp: new Date(1000 * payload.exp),
  };
}
*/
