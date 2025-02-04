import functools
import typing

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
    return functools.partial(
        _concatenated,
        f = f,
        g = g,
    )

def _concatenated[S, T, U](
    initial: S,
    f: typing.Callable[[S], T],
    g: typing.Callable[[T], U],
) -> U:
    return g(f(initial))

def map_over[S, T](
    function: typing.Callable[[S], T],
) -> typing.Callable[[typing.Sequence[S]], list[T]]:
    return functools.partial(
        _mapped_over,
        function = function,
    )

def _mapped_over[S, T](
    initial: typing.Sequence[S],
    function: typing.Callable[[S], T],
) -> list[T]:
    return [function(s) for s in initial]

def getattr_from(
    o: object,
    name: str,
):
    return getattr(o, name)
