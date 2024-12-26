"use server"

import { client, Item, likeItemsLikePut, LikeStatus, loginTokenPost, rootItemsGet } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL})

const token = await loginTokenPost({
  "body": {
    "username": process.env.API_USERNAME!,
    "password": process.env.API_PASSWORD!,
  },
});

if (token.error) {
  throw token.error;
}

client.interceptors.request.use((request, options) => {
  request.headers.set("Authorization", `Bearer ${token.data.access_token}`);
  return request;
});

export async function doLikeItemsLikePut(item: Item, score: LikeStatus) {
  const resp = await likeItemsLikePut({
    "query": {
      "item_id": item.id,
      "score": score,
    },
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function doRootItemsGet(
  dt_from: Date,
  dt_to: Date,
): Promise<Item[]> {
  const items_response = await rootItemsGet({
    "query": {
      "dt_from": dt_from.toISOString(),
      "dt_to": dt_to.toISOString(),
    },
  });

  if (items_response.error) {
    throw items_response.error;
  }

  return items_response.data;
}
