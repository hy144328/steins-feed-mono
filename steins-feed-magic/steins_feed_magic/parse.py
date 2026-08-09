import lxml.etree
import lxml.html

def text_content(s: str) -> str:
    queue: list[lxml.html.HtmlElement | str] = []
    res: list[str] = []

    try:
        tree = lxml.html.fromstring(s)
        queue.append(tree)
    except lxml.etree.ParserError:  # pragma: no cover
        return ""

    while len(queue) > 0:
        node_it = queue.pop()

        if isinstance(node_it, str):
            res.append(node_it)
            continue

        for child_it in reversed(node_it):
            if child_it.tail is not None:
                queue.append(child_it.tail)

            queue.append(child_it)

        if node_it.text is not None:
            queue.append(node_it.text)

    return "".join(res)
