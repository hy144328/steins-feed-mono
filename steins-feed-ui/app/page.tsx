import { client, rootItemsGet } from "@client"
import { join } from "@util"

import WallArticle from "./components"

export default async function Page() {
  client.setConfig({"baseUrl": "http://localhost:8000"});

  const items_response = await rootItemsGet({
    "query": {
      "dt_from": new Date(1970, 1, 1).toISOString(),
      "dt_to": new Date(2025, 1, 1).toISOString(),
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
