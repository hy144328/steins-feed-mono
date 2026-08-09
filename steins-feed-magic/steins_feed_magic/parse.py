import lxml.etree
import lxml.html

def text_content(s: str) -> str:
    stack: list[lxml.html.HtmlElement | str] = []
    res: list[str] = []

    try:
        tree = lxml.html.fromstring(s)
        stack.append(tree)
    except lxml.etree.ParserError:  # pragma: no cover
        return ""

    while len(stack) > 0:
        node_it = stack.pop()

        if isinstance(node_it, str):
            res.append(node_it)
            continue

        for child_it in reversed(node_it):
            if child_it.tail is not None:
                stack.append(child_it.tail)

            stack.append(child_it)

        if node_it.text is not None:
            stack.append(node_it.text)

    return "".join(res)
