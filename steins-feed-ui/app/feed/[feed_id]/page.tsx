import { Language } from "@client"

import Navigation from "../../navigation"

import { FeedForm, TagsForm } from "./components"

export default async function Page({
  params,
}: {
  params: Promise<{feed_id: number}>,
}) {
  const feed = {
    id: 1,
    title: "The Atlantic",
    link: "https://www.theatlantic.com/",
    language: "Swedish" as Language,
    tags: [],
  };
  const tags = [
    {
      id: 1,
      name: "news",
    },
    {
      id: 2,
      name: "magazine",
    },
  ];
  const all_tags = [
    {
      id: 1,
      name: "news",
    },
    {
      id: 2,
      name: "magazine",
    },
    {
      id: 3,
      name: "politics",
    },
  ]

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
    tags={ tags }
    all_tags={ all_tags }
  />
</div>
  )
}
