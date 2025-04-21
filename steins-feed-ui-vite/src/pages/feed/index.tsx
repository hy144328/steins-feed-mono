import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router"

import { Feed } from "@/client"
import { feedFeedsFeedFeedIdGet } from "@/client"

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

  <TagsForm feed={ feed }/>
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
