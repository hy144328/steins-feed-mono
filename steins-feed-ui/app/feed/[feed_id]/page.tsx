import Navigation from "../../navigation"

import { doFeed, doTags } from "./actions"
import { FeedForm, TagsForm } from "./components"

export default async function Page({
  params,
}: {
  params: Promise<{feed_id: number}>,
}) {
  const paramsSync = await params;
  const feed = await doFeed(paramsSync.feed_id);
  const all_tags = await doTags();

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
