export function text_content(s: string): string {
  const res: Text[] = [];

  for (const node_it of iterate_deep(parse_body(s))) {
    if (node_it.nodeType === Node.TEXT_NODE) {
      res.push(node_it as Text);
    }
  }

  return res.map(x => x.nodeValue).join("");
}

export function wrap_word(
  s: string,
  word: string,
  wrap: (arg0: string) => Node,
  ignore_case: boolean = false,
  full_match: boolean = false,
): string {
  const body = parse_body(s);
  const res: {node: Text, start: number, finish: number}[] = [];
  let last_idx = 0;

  for (const node_it of iterate_deep(body)) {
    if (node_it.nodeType !== Node.TEXT_NODE) {
      continue;
    }

    const res_it = {
      node: node_it as Text,
      start: last_idx,
      finish: last_idx + node_it.nodeValue!.length,
    };

    res.push(res_it);
    last_idx += node_it.nodeValue!.length;
  }

  const full_text = res.map(x => x.node.nodeValue).join("");
  const re_pat = full_match ? `\\b${word}\\b` : word;
  const re_flags = ignore_case ? "gi" : "g";
  const re = new RegExp(re_pat, re_flags);

  for (const match_it of full_text.matchAll(re)) {
    const res_match = res.filter(res_it =>
      (res_it.finish > match_it.index) && (res_it.start < match_it.index + word.length)
    );

    for (const res_it of res_match) {
      let node_it = res_it.node;

      if (res_it.finish > match_it.index + word.length) {
        node_it.splitText(match_it.index + word.length - res_it.start);
      }

      if (res_it.start < match_it.index) {
        node_it.splitText(match_it.index - res_it.start);
        node_it = node_it.nextSibling as Text;
      }

      replace_node(node_it, wrap(node_it.nodeValue!));
    }
  }

  return body.innerHTML;
}

function parse_body(s: string): HTMLElement {
  const parser = new DOMParser();
  const root = parser.parseFromString(s, "text/html");
  return root.body;
}

function* iterate_deep(node: Node): Generator<Node> {
  const que: Node[] = [node];

  while (que.length > 0) {
    const node_it = que.pop()!;

    for (const child_it of Array.from(node_it.childNodes).reverse()) {
      que.push(child_it);
    }

    yield node_it;
  }
}

function replace_node(node: Node, ...nodes: Node[]) {
  for (const node_it of nodes) {
    node.parentNode!.insertBefore(node_it, node);
  }

  node.parentNode!.removeChild(node);
}
