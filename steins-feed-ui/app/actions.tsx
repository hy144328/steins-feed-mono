"use server"

import { cookies } from "next/headers"

import { client, Item, likeItemsLikePut, LikeStatus, rootItemsGet } from "@client"

client.setConfig({"baseUrl": process.env.API_BASE_URL});

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
  const cookie_store = await cookies();
  const cookie = cookie_store.get("api_token");

  if (!cookie) {
    throw {"detail": "Not authenticated"};
  }

  client.interceptors.request.use(request => {
    request.headers.set("Authorization", `Bearer ${cookie.value}`);
    return request;
  });

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
