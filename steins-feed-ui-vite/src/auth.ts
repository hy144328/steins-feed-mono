import Cookies from "js-cookie"
import { NavigateFunction } from "react-router"

import { client } from "@/client/client.gen"

client.setConfig({"baseUrl": import.meta.env.VITE_API_BASE_URL});

export async function logout() {
  Cookies.remove("api_token");
}

export async function authenticate() {
  const cookie = Cookies.get("api_token");

  if (!cookie) {
    throw {"detail": "Not authenticated"};
  }

  client.interceptors.request.use(request => {
    request.headers.set("Authorization", `Bearer ${cookie}`);
    return request;
  });
}

export function require_login(
  navigate: NavigateFunction,
  pathname: string,
) {
  navigate(`/login?pathname=${encodeURIComponent(pathname)}`);
}

export function skip_login_if_unnecessary(
  navigate: NavigateFunction,
  pathname: string,
) {
  const cookie = Cookies.get("api_token");

  if (!cookie) {
    return;
  }

  const payload = decode_jwt(cookie);
  if (payload.exp <= new Date()) {
    return;
  }

  navigate(pathname);
}

function decode_jwt(token: string): {sub: string, exp: Date} {
  const payload_enc = token.split(".")[1];
  const payload_dec = atob(payload_enc);
  const payload = JSON.parse(payload_dec);

  return {
    sub: payload.sub,
    exp: new Date(1000 * payload.exp),
  };
}
