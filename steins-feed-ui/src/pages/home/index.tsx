import { memo, useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router"

import { Item, Language, WallMode } from "@/client"
import { rootItemsGet, lastUpdatedItemsLastUpdatedGet } from "@/client"

import { authenticate, require_login } from "@/auth"
import Graph from "@/graph"
import { similar_edit } from "@/metrics"
import {
  day_of_week_short,
  ensure_array,
  ensure_primitive,
  format_datetime,
  month_of_year_short
} from "@/util"

import WallArticle from "./article"
import Navigation from "./navigation"
import { toURLSearchParams } from "./util"

export default function Page() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const now_raw = searchParams.get("now");
  const now = now_raw ? new Date(ensure_primitive(now_raw)) : new Date();

  const today = new Date(now);
  today.setUTCHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setUTCDate(today.getUTCDate() + 1);

  const languages = ensure_array(searchParams.getAll("languages")).map(lang_it => lang_it as Language);
  const tags = ensure_array(searchParams.getAll("tags")).map(tag_it => parseInt(tag_it as string));

  const wall_mode_raw = searchParams.get("wall_mode");
  const wall_mode = wall_mode_raw ? ensure_primitive(wall_mode_raw) as WallMode : "Classic";

  const [items, setItems] = useState<Item[]>([]);
  const [lastPublished, setLastPublished] = useState(new Date(0));

  useEffect(() => {
    async function loadItems() {
      try {
        setItems(await getItems(today, tomorrow, languages, tags, wall_mode));
      } catch (e) {
        console.log(e);
        require_login(navigate, `/?${toURLSearchParams({now, languages, tags, wall_mode})}`);
      }
    }

    lastUpdated(languages, tags).then(d => setLastPublished(d));
    loadItems();
  }, [searchParams])

  return (
<div className="container">
<Navigation
  now={ now }
  languages={ languages }
  tags={ tags }
  wall_mode={ wall_mode }
  contentServed={ true }
/>
<Header now={ now } last_published={ lastPublished } items={ items }/>
<hr/>
<Main items={ items }/>
<hr/>
<Footer/>
</div>
  );
}

function Header({
  now,
  last_published,
  items,
}: {
  now: Date,
  last_published: Date,
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
Last published: { format_datetime(last_published) }.
</p>
</header>
  );
}

function Footer() {
  return (
<footer>
<a href="https://github.com/steins-feed/steins-feed-mono">GitHub</a>
</footer>
  );
}

const WallArticleMemo = memo(WallArticle);

function Main({
  items,
}: {
  items: Item[],
}) {
  console.log("Start represent_cluster.", new Date());
  const [itemsRepr, setItemsRepr] = useState(Array<Item | undefined>(items.length).fill(undefined));
  const res = items.map((item_it, item_ct) =>
    <WallArticleMemo
      item={ item_it }
      original={ itemsRepr[item_ct] }
      key={ `article_${item_it.id}` }
    />
  );
  console.log("Finish represent_cluster.", new Date());

  useEffect(() => {
    setItemsRepr(pick_representatives(items));
  }, [items]);

  return (
<main>
{ res }
</main>
  );
}

function pick_representatives(
  items: Item[],
): (Item | undefined)[] {
  const g = new Graph<number>();

  for (let i = 0; i < items.length; i++) {
    g.add_node(i);
  }

  for (let i = 0; i < items.length; i++) {
    for (let j = i+1; j < items.length; j++) {
      const title_i = items[i].title;
      const title_j = items[j].title;

      if (similar_edit(title_i, title_j, 0.05 * Math.min(title_i.length, title_j.length))) {
        g.add_edge(i, j);
      }
    }
  }

  console.log("Find clusters.", new Date());
  const clusters = g.clusters();
  console.log("Find clusters finished.", new Date());
  console.log("Find representatives of clusters.", new Date());
  const entries_repr = Array.from(clusters).flatMap(cluster_it => {
    const array_it = Array.from(cluster_it);
    const item_ct_min = array_it.reduce((prev_ct, curr_ct) => {
      const prev_dt = items[prev_ct].published;
      const curr_dt = items[curr_ct].published;

      if (prev_dt < curr_dt) {
        return curr_ct;
      } else if (prev_dt > curr_dt) {
        return prev_ct;
      } else {
        return (prev_ct < curr_ct) ? prev_ct : curr_ct;
      }
    });
    return array_it.map(item_ct => [item_ct, item_ct_min])
  });
  const dict_repr = Object.fromEntries(entries_repr) as Record<number, number>;

  return items.map((_, item_ct) => {
    const repr_ct = dict_repr[item_ct];
    const repr_it = items[repr_ct];
    return (item_ct === repr_ct) ? undefined : repr_it;
  });
}

async function getItems(
  dt_from: Date,
  dt_to: Date,
  languages?: Language[],
  tags?: number[],
  wall_mode?: WallMode,
): Promise<Item[]> {
  await authenticate();

  const resp = await rootItemsGet({
    query: {
      dt_from: dt_from.toISOString(),
      dt_to: dt_to.toISOString(),
      languages: languages,
      tags: tags,
      wall_mode: wall_mode,
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

async function lastUpdated(
  languages?: Language[],
  tags?: number[],
): Promise<Date> {
  await authenticate();

  const resp = await lastUpdatedItemsLastUpdatedGet({
    query: {
      languages: languages,
      tags: tags,
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return new Date(resp.data);
}
