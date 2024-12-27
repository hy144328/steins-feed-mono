import Container from "react-bootstrap/Container"

import { Item } from "@client"
import { day_of_week_short, format_datetime, month_of_year_short } from "@util"

import { doRootItemsGet } from "./actions"
import WallArticle from "./components"
import Navigation from "./navigation"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{"now": string | undefined}>
}) {
  const now = new Date((await searchParams).now ?? new Date());
  const today = new Date(now);
  today.setUTCHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setUTCDate(today.getUTCDate() + 1);

  const items = await doRootItemsGet(today, tomorrow);

  return (
<Container>
<Navigation/>
<Header now={ now } items={ items }/>
<hr/>
<Main items={ items }/>
<hr/>
<Footer/>
</Container>
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

  return (
<main>
{
    items.map(item_it => <WallArticle item={ item_it } key={ `article_${item_it.id}` }/>)
}
</main>
  );
}
