export default class Graph<K extends string | number | symbol> {
  nodes: Set<K> = new Set<K>();
  edges: Record<K, Set<K>> = {} as Record<K, Set<K>>;

  add_node(k: K) {
    this.nodes.add(k);
  }

  add_edge(k: K, l: K) {
    if (!(k in this.edges)) {
      this.edges[k] = new Set();
    }

    if (!(l in this.edges)) {
      this.edges[l] = new Set();
    }

    this.edges[k].add(l);
    this.edges[l].add(k);
  }

  neighbors(k: K): Set<K> {
    return this.edges[k];
  }

  clusters(): Set<Set<K>> {
    const res = new Set<Set<K>>();
    const nodes = new Set(this.nodes);

    while (nodes.size !== 0) {
      const k = pop(nodes)!;
      res.add(this.cluster(k, nodes));
    }

    return res;
  }

  cluster(k: K, nodes: Set<K>): Set<K> {
    const res = new Set<K>();
    const que = [k];

    while (que.length !== 0) {
      const kIt = que.shift()!;
      res.add(kIt);
      nodes.delete(kIt);

      for (const neighbor_it of this.neighbors(k)) {
        if (nodes.has(neighbor_it)) {
          que.push(neighbor_it);
        }
      }
    }

    return res;
  }
}

function pop<K>(coll: Set<K>): K | undefined {
  for (const k of coll) {
    coll.delete(k);
    return k;
  }
}
