"use server"

import { Item, Language, LikeStatus, Tag, WallMode } from "@client"
import { languagesFeedsLanguagesGet, likeItemsLikePut, rootItemsGet, tagsFeedsTagsGet } from "@client"

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
  languages?: Language[],
  tags?: number[],
  wall_mode?: WallMode,
): Promise<Item[]> {
  await authenticate();

  const resp = await rootItemsGet({
    query: {
      dt_from: dt_from.toISOString(),
      dt_to: dt_to.toISOString(),
      languages: languages,
      tags: tags,
      wall_mode: wall_mode,
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
