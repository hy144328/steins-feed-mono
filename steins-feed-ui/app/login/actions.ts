"use server"

import { cookies } from "next/headers"

import { client, loginTokenPost } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL});

export async function doLoginTokenPost(
  username: string,
  password: string
) {
  const cookie_store = await cookies();
  const token = await loginTokenPost({
    "body": {
      "username": username,
      "password": password,
    },
  });

  if (token.error) {
    throw token.error;
  }

  cookie_store.set("api_token", token.data.access_token);
}
