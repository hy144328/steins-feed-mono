"use server"

import {
  Item,
  Language,
  LikeStatus,
  Tag,
  WallMode,
} from "@client"
import {
  analyzeSummaryItemsAnalyzeSummaryGet,
  analyzeTitleItemsAnalyzeTitleGet,
  languagesFeedsLanguagesGet,
  likeItemsLikePut,
  rootItemsGet,
  tagsFeedsTagsGet,
} from "@client"

import { authenticate } from "./auth"

export async function putLikeAction(item_id: number, score: LikeStatus) {
  await authenticate();

  const resp = await likeItemsLikePut({
    "query": {
      "item_id": item_id,
      "score": score,
    },
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function getItemsAction(
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

export async function getLanguagesAction(): Promise<Language[]> {
  await authenticate();

  const resp = await languagesFeedsLanguagesGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}

export async function getTagsAction(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}

export async function analyzeTitleAction(
  item_id: number,
): Promise<Record<string, number>> {
  await authenticate();

  const resp = await analyzeTitleItemsAnalyzeTitleGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

export async function analyzeSummaryAction(
  item_id: number,
): Promise<Record<string, number>> {
  await authenticate();

  const resp = await analyzeSummaryItemsAnalyzeSummaryGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
