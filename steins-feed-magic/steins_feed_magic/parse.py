import lxml.etree
import lxml.html

def text_content(s: str) -> str:
    try:
        tree = lxml.html.fromstring(s)
        res = tree.text_content()
    except lxml.etree.ParserError:  # pragma: no cover
        res = ""

    return res
