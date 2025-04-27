import { memo, useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router"

import { Item, Language, WallMode } from "@/client"
import { rootItemsGet, lastUpdatedItemsLastUpdatedGet } from "@/client"

import { authenticate, require_login } from "@/auth"
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
  const [itemsRepr, setItemsRepr] = useState(Array<Item | undefined>(items.length).fill(undefined));
  const res = items.map((item_it, item_ct) =>
    <WallArticleMemo
      item={ item_it }
      original={ itemsRepr[item_ct] }
      key={ `article_${item_it.id}` }
    />
  );

  useEffect(() => {
    const worker = new Worker(new URL("./worker.ts", import.meta.url), {type: "module"});
    pick_representatives(worker, items, setItemsRepr);
    return () => {worker.terminate()};
  }, [items]);

  return (
<main>
{ res }
</main>
  );
}

function pick_representatives(
  worker: Worker,
  items: Item[],
  setItems: (is: (Item | undefined)[]) => void,
) {
  worker.onmessage = (e: MessageEvent<number[]>) => {
    const items_repr = e.data;
    const res = items.map((_, item_ct) => {
      const repr_ct = items_repr[item_ct];
      const repr_it = items[repr_ct];
      return (item_ct === repr_ct) ? undefined : repr_it;
    });
    setItems(res);
  };

  worker.postMessage(items.map(item_it => {
    return {title: item_it.title, published: item_it.published}
  }));
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
