export function text_content(s: string): string {
  const parser = new DOMParser();
  const root = parser.parseFromString(s, "text/html");
  const que: Node[] = [root.body];
  const res: Node[] = [];

  while (que.length > 0) {
    const node_it = que.pop()!;

    for (const child_it of Array.from(node_it.childNodes).reverse()) {
      que.push(child_it);
    }

    if (node_it.nodeType !== Node.TEXT_NODE) {
      continue;
    }

    res.push(node_it);
  }

  return res.map(x => x.nodeValue).join("");
}
