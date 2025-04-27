import Graph from "@/graph"
import { similar_edit } from "@/metrics"

self.onmessage = (e: MessageEvent<{title: string, published: Date}[]>) => {
  const items = e.data;
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

  const clusters = g.clusters();
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

  self.postMessage(items.map((_, item_ct) => dict_repr[item_ct]));
};
