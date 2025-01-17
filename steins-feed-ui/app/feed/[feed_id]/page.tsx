import { feedFeedsFeedFeedIdGet, tagsFeedsTagsGet } from "@client"

import Navigation from "../../navigation"

import { FeedForm, TagsForm } from "./components"

export default async function Page({
  params,
}: {
  params: Promise<{feed_id: number}>,
}) {
  const paramsSync = await params;

  const feed_resp = await feedFeedsFeedFeedIdGet({path: {feed_id: paramsSync.feed_id}});
  if (feed_resp.error) {
    throw feed_resp.error;
  }

  const all_tags_resp = await tagsFeedsTagsGet();
  if (all_tags_resp.error) {
    throw all_tags_resp.error;
  }

  const feed = feed_resp.data;
  const all_tags = all_tags_resp.data!;

  return (
<div className="container">
  <Navigation
    now={ new Date(0) }
    languages={ [] }
    tags={ [] }
    contentServed={ false }
  />

  <h1>Feed</h1>

  <FeedForm
    feed={ feed }
    all_languages={ ["English", "German", "Swedish"] }
  />

  <hr/>

  <TagsForm
    feed ={ feed }
    all_tags={ all_tags }
  />
</div>
  )
}
