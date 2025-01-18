"use server"

import { Feed, Tag } from "@client"
import {
  attachTagFeedsFeedFeedIdAttachTagPut,
  attachUserFeedsFeedFeedIdAttachUserPut,
  createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut,
  detachTagFeedsFeedFeedIdDetachTagDelete,
  detachUserFeedsFeedFeedIdDetachUserDelete,
} from "@client"
import {
  feedFeedsFeedFeedIdGet,
  tagsFeedsTagsGet,
} from "@client"


import { authenticate } from "../../auth"

export async function doCreateAndAttachTag(
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

export async function doAttachTag(
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

export async function doDetachTag(
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

export async function doAttachUser(
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

export async function doDetachUser(
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

export async function doFeed(
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

export async function doTags(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (resp.error) {
    throw resp.error;
  }

  return resp.data ?? [];
}
