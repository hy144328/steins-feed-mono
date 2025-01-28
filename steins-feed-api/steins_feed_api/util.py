import concurrent.futures
import queue
import typing

def to_iterator[T](
    queue: queue.Queue[T],
    sentinel: typing.Any = None,
) -> typing.Iterator[T]:
    return iter(queue.get, sentinel)

def close_queue_when_done(
    queue_in: queue.Queue,
    queue_out: queue.Queue,
    sentinel: typing.Any = None,
):
    queue_in.join()
    queue_out.put(sentinel)

def from_queue_to_queue[T](
    queue_in: queue.Queue,
    queue_out: queue.Queue[T],
    sentinel: typing.Any = None,
) -> typing.Generator[T]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(
            close_queue_when_done,
            queue_in = queue_in,
            queue_out = queue_out,
            sentinel = sentinel,
        )

        yield from to_iterator(queue_out, sentinel=sentinel)

def to_queue[**P, T](
    q: queue.Queue[T],
    task_done: typing.Optional[typing.Callable[[], None]] = None,
) -> typing.Callable[[typing.Callable[P, typing.Generator[T]]], typing.Callable[P, None]]:
    def wrapper(
        res: typing.Callable[P, typing.Generator[T]],
    ) -> typing.Callable[P, None]:
        def wrapped(*args: P.args, **kwargs: P.kwargs):
            for res_it in res(*args, **kwargs):
                q.put(res_it)

            if task_done is not None:
                task_done()

        return wrapped

    return wrapper
