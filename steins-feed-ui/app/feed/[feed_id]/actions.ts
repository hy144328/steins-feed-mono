"use server"

import { Feed, Language, Tag } from "@client"
import {
  attachTagFeedsFeedFeedIdAttachTagPut,
  attachUserFeedsFeedFeedIdAttachUserPut,
  createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut,
  detachTagFeedsFeedFeedIdDetachTagDelete,
  detachUserFeedsFeedFeedIdDetachUserDelete,
  feedFeedsFeedFeedIdGet,
  tagsFeedsTagsGet,
  updateFeedFeedsFeedFeedIdUpdateFeedPost,
} from "@client"


import { authenticate } from "../../auth"

export async function createAndAttachTagAction(
  feed_id: number,
  tag_name: string,
): Promise<Tag> {
  await authenticate();

  const resp = await createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut({
    path: {feed_id: feed_id},
    query: {tag_name: tag_name},
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

export async function attachTagAction(
  feed_id: number,
  tag_id: number,
) {
  await authenticate();

  const resp = await attachTagFeedsFeedFeedIdAttachTagPut({
    path: {feed_id: feed_id},
    query: {tag_id: tag_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function detachTagAction(
  feed_id: number,
  tag_id: number,
) {
  await authenticate();

  const resp = await detachTagFeedsFeedFeedIdDetachTagDelete({
    path: {feed_id: feed_id},
    query: {tag_id: tag_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function attachUserAction(
  feed_id: number,
) {
  await authenticate();

  const resp = await attachUserFeedsFeedFeedIdAttachUserPut({
    path: {feed_id: feed_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function detachUserAction(
  feed_id: number,
) {
  await authenticate();

  const resp = await detachUserFeedsFeedFeedIdDetachUserDelete({
    path: {feed_id: feed_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

export async function getFeedAction(
  feed_id: number,
): Promise<Feed> {
  await authenticate();

  const resp = await feedFeedsFeedFeedIdGet({
    path: {feed_id: feed_id},
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

export async function getTagsAction(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (resp.error) {
    throw resp.error;
  }

  return resp.data ?? [];
}

export async function updateFeedAction(
  feed_id: number,
  title: string,
  link: string,
  language: Language | null,
): Promise<Feed> {
  await authenticate();

  const resp = await updateFeedFeedsFeedFeedIdUpdateFeedPost({
    path: {feed_id: feed_id},
    query: {
      title: title,
      link: link,
      ...(language ? {language: language}: {}),
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
