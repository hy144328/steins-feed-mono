import collections

import lxml.etree
import lxml.html

def text_content(s: str) -> str:
    que = collections.deque[lxml.html.HtmlElement | str]()
    res = []

    try:
        tree = lxml.html.fromstring(s)
        que.append(tree)
    except lxml.etree.ParserError:  # pragma: no cover
        return ""

    while len(que) > 0:
        node_it = que.pop()

        if isinstance(node_it, str):
            res.append(node_it)
            continue

        for child_it in reversed(node_it):
            if child_it.tail is not None:
                que.append(child_it.tail)

            que.append(child_it)

        if node_it.text is not None:
            que.append(node_it.text)

    return "".join(res)
