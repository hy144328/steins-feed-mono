import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router"

import { Feed, Tag } from "@/client"
import {
  feedFeedsFeedFeedIdGet,
  tagsFeedsTagsGet,
} from "@/client"

import { authenticate, require_login } from "@/auth"
import Navigation from "@/pages/home/navigation"

import DisplayForm from "./display"
import FeedForm from "./feed"
import TagsForm from "./tags"

export default function Page() {
  const params = useParams();
  const feed_id = parseInt(params.feed_id!);
  const navigate = useNavigate();

  const [feed, setFeed] = useState<Feed>({
    id: -1,
    title: "",
    link: "",
    language: null,
    tags: [],
    displayed: false,
  });
  const [allTags, setAllTags] = useState<Tag[]>([]);

  useEffect(() => {
    async function loadFeed() {
      try {
        setFeed(await getFeed(feed_id));
      } catch (e) {
        console.log(e);
        require_login(navigate, `/feed/${feed_id}`);
      }
    }

    loadFeed();
  }, []);
  useEffect(() => {
    async function loadTags() {
      try {
        setAllTags(await getTags());
      } catch (e) {
        console.log(e);
        require_login(navigate, `/feed/${feed_id}`);
      }
    }

    loadTags();
  }, []);

  return (
<div className="container">
  <Navigation
    now={ new Date(0) }
    languages={ [] }
    tags={ [] }
    contentServed={ false }
  />

  <DisplayForm feed={ feed }/>

  <FeedForm
    feed={ feed }
    all_languages={ ["English", "German", "Swedish"] }
    is_admin={ true }
  />

  <hr/>

  <TagsForm
    feed ={ feed }
    all_tags={ allTags }
  />
</div>
  )
}

async function getFeed(
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

async function getTags(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (resp.error) {
    throw resp.error;
  }

  return resp.data ?? [];
}
