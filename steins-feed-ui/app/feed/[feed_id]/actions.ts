"use server"

import { Tag } from "@client"
import { attachTagFeedsFeedFeedIdAttachTagPut, createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut, detachTagFeedsFeedFeedIdDetachTagDelete } from "@client"

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
