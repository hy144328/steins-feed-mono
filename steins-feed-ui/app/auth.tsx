"use server"

import { cookies } from "next/headers"

import { client } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL});

export async function logout() {
  const cookie_store = await cookies();
  cookie_store.delete("api_token");
}

export async function authenticate() {
  const cookie_store = await cookies();
  const cookie = cookie_store.get("api_token");

  if (!cookie) {
    throw {"detail": "Not authenticated"};
  }

  client.interceptors.request.use(request => {
    request.headers.set("Authorization", `Bearer ${cookie.value}`);
    return request;
  });
}
