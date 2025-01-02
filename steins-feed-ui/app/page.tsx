import { Item, Language } from "@client"
import {
  day_of_week_short,
  ensure_array,
  ensure_primitive,
  format_datetime,
  group_by,
  month_of_year_short
} from "@util"

import { doRootItemsGet } from "./actions"
import { require_login } from "./auth"
import WallArticle from "./components"
import Navigation from "./navigation"
import { toURLSearchParams } from "./util"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{[key: string]: undefined | string | string[]}>,
}) {
  const searchParamsSync = await searchParams;

  const now_raw = searchParamsSync.now;
  const now = now_raw ? new Date(ensure_primitive(now_raw)) : new Date();

  const today = new Date(now);
  today.setUTCHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setUTCDate(today.getUTCDate() + 1);

  const languages = ensure_array(searchParamsSync.languages).map(lang_it => lang_it as Language);
  const tags = ensure_array(searchParamsSync.tags).map(tag_it => parseInt(tag_it));

  let items: Array<Item> = [];
  try {
    items = await doRootItemsGet(today, tomorrow, languages, tags);
  } catch (e) {
    console.log(e);
    await require_login(`/?${toURLSearchParams({now, languages, tags})}`);
  }

  return (
<div className="container">
<Navigation
  now={ now }
  languages={ languages }
  tags={ tags }
/>
<Header now={ now } items={ items }/>
<hr/>
<Main items={ items }/>
<hr/>
<Footer/>
</div>
  );
}

async function Header({
  now,
  items,
}: {
  now: Date,
  items: Item[],
}) {
  const day = now.getUTCDate();
  const month = now.getUTCMonth();
  const year = now.getUTCFullYear();

  const last_published = new Date((items.length > 0) ? items[0].published : 0);

  return (
<header>
<h1>{ day_of_week_short[now.getUTCDay()] }, { day }. { month_of_year_short[month] } { year }</h1>
<p>
{ items.length } articles.
Last published: { format_datetime(last_published) }.
</p>
</header>
  );
}

async function Footer() {
  return (
<footer>
<a href="https://github.com/steins-feed/steins-feed-mono">GitHub</a>
</footer>
  );
}

async function Main({
  items,
}: {
  items: Item[],
}) {
  const items_grouped = group_by(
    items,
    (a, b) => (a.published === b.published) && (a.title == b.title)
  );
  const res = items_grouped.flatMap(item_group_it =>
    item_group_it.map((item_it, item_ct) =>
      <WallArticle
        item={ item_it }
        original={ item_ct === 0 ? undefined : item_group_it[0] }
        key={ `article_${item_it.id}` }
      />
    )
  );

  return (
<main>
{ res }
</main>
  );
}
