"use server"

import { client, loginTokenPost } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL})

export async function doLoginTokenPost(
  username: string,
  password: string
) {
  const token = await loginTokenPost({
    "body": {
      "username": username,
      "password": password,
    },
  });

  if (token.error) {
    throw token.error;
  }

  client.interceptors.request.use((request, options) => {
    request.headers.set("Authorization", `Bearer ${token.data.access_token}`);
    return request;
  });
}
