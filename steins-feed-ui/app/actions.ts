"use server"

import { Item, likeItemsLikePut, LikeStatus, rootItemsGet } from "@client"

import { authenticate } from "./auth"

export async function doLikeItemsLikePut(item: Item, score: LikeStatus) {
  await authenticate();

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
  await authenticate();

  const resp = await rootItemsGet({
    "query": {
      "dt_from": dt_from.toISOString(),
      "dt_to": dt_to.toISOString(),
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
