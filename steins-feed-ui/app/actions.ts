"use server"

import { Item, Language, LikeStatus, languagesFeedsLanguagesGet, likeItemsLikePut, rootItemsGet, Tag, tagsFeedsTagsGet } from "@client"

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

export async function doLanguagesFeedsLangaugesGet(): Promise<Language[]> {
  await authenticate();

  const resp = await languagesFeedsLanguagesGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}

export async function doTagsFeedsTagsGet(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}
