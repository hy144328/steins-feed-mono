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

def fold_left[S, T](
    initial: S,
    sequence: typing.Sequence[T],
    function: typing.Callable[[S, T], S],
) -> S:
    return functools.reduce(
        function,
        sequence,
        initial,
    )

def apply_to[S, T](
    initial: S,
    function: typing.Callable[[S], T],
) -> T:
    return function(initial)

def chain[T](*funcs: typing.Callable[[T], T]) -> typing.Callable[[T], T]:
    return functools.partial(
        fold_left,
        function = apply_to,
        sequence = funcs,
    )

def concatenate[S, T, U](
    f: typing.Callable[[S], T],
    g: typing.Callable[[T], U],
) -> typing.Callable[[S], U]:
    def concatenated(
        initial: S,
        f: typing.Callable[[S], T],
        g: typing.Callable[[T], U],
    ) -> U:
        return g(f(initial))

    return functools.partial(
        concatenated,
        f = f,
        g = g,
    )

def map_over[S, T](
    function: typing.Callable[[S], T],
) -> typing.Callable[[typing.Sequence[S]], list[T]]:
    def mapped_over(
        initial: typing.Sequence[S],
        function: typing.Callable[[S], T],
    ) -> list[T]:
        return [function(s) for s in initial]

    return functools.partial(
        mapped_over,
        function = function,
    )
