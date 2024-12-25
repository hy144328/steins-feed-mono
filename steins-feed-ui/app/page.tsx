import { client, Item, rootItemsGet } from "@client"
import { day_of_week_short, format_datetime, join, month_of_year_short } from "@util"

import WallArticle from "./components"

export default async function Page() {
  client.setConfig({"baseUrl": "http://localhost:8000"});

  const now = new Date();
  const today = new Date(now);
  today.setUTCHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setUTCDate(today.getUTCDate() + 1);

  const items_response = await rootItemsGet({
    "query": {
      "dt_from": today.toISOString(),
      "dt_to": tomorrow.toISOString(),
    },
  });

  if (!items_response.data) {
    throw items_response.error;
  }

  return (
<>
<Header now={ now } items={ items_response.data }/>
<hr />
<Main items={ items_response.data }/>
<hr />
<Footer/>
</>
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

  return (
<header>
<h1>{ day_of_week_short[now.getUTCDay()] }, { day }. { month_of_year_short[month] } { year }</h1>
<p>
{ items.length } articles.
Last published: { format_datetime(new Date(items[0].published)) }.
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
  join(
    items.map(item_it => <WallArticle item={ item_it } key={ `article_${item_it.id}` }/>),
    article_ct => <hr className="article-hr" key={ `article_hr_${article_ct}` }/>,
  )
}
</main>
  );
}
