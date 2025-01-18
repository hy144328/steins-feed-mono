import { Feed, Tag } from "@client"

import Navigation from "../../navigation"

import { doFeed, doTags } from "./actions"
import { require_login } from "../../auth"
import { DisplayForm, FeedForm, TagsForm } from "./components"

export default async function Page({
  params,
}: {
  params: Promise<{feed_id: number}>,
}) {
  const paramsSync = await params;

  let feed: Feed | undefined = undefined;
  let all_tags: Tag[] = [];

  try {
    feed = await doFeed(paramsSync.feed_id);
    all_tags = await doTags();
  } catch (e) {
    console.log(e);
    await require_login(`/feed/${paramsSync.feed_id}`);
  }

  return (
<div className="container">
  <Navigation
    now={ new Date(0) }
    languages={ [] }
    tags={ [] }
    contentServed={ false }
  />

  <DisplayForm feed={ feed! }/>

  <FeedForm
    feed={ feed! }
    all_languages={ ["English", "German", "Swedish"] }
  />

  <hr/>

  <TagsForm
    feed ={ feed! }
    all_tags={ all_tags }
  />
</div>
  )
}
