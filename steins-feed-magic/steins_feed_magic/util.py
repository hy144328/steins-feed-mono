import functools
import typing

import lxml.etree
import lxml.html

def text_content(s: str) -> str:
    try:
        tree = lxml.html.fromstring(s)
        res = tree.text_content()
    except lxml.etree.ParserError:
        res = ""

    return res

def chain[T](*funcs: typing.Callable[[T], T]) -> typing.Callable[[T], T]:
    return lambda s: functools.reduce(
        lambda x, f: f(x),
        funcs,
        s,
    )
