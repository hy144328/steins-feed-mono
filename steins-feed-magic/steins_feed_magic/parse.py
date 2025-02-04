import collections

import lxml.etree
import lxml.html

class HtmlElementTail(lxml.html.HtmlElement):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

def text_content(s: str) -> str:
    que = collections.deque[lxml.html.HtmlElement]()
    res = []

    try:
        tree = lxml.html.fromstring(s)
        que.append(tree)
    except lxml.etree.ParserError:  # pragma: no cover
        return ""

    while len(que) > 0:
        node_it = que.pop()

        if node_it.text is not None:
            res.append(node_it.text)

        for child_it in reversed(node_it):
            if child_it.tail is not None:
                que.append(HtmlElementTail(child_it.tail))

            que.append(child_it)

    return "".join(res)
