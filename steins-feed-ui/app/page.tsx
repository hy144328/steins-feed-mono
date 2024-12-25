import { client, rootItemsGet } from "@client"
import { join } from "@util"

import WallArticle from "./components"

export default async function Page() {
  client.setConfig({"baseUrl": "http://localhost:8000"});

  const now = new Date();
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  const items_response = await rootItemsGet({
    "query": {
      "dt_from": today.toISOString(),
      "dt_to": tomorrow.toISOString(),
    },
  });

  if (!items_response.data) {
    throw items_response.error;
  }

  const articles_hr = join(
    items_response.data.map(item_it =>
      <WallArticle item={ item_it } key={ `article_${item_it.id}` }/>
    ),
    article_ct => <hr className="article-hr" key={ `article_hr_${article_ct}` }/>,
  );

  return <>{ articles_hr }</>;
}
