import concurrent.futures
import queue
import typing

def to_iterator[T](
    queue: queue.Queue[T],
    sentinel: typing.Any = None,
) -> typing.Iterator[T]:
    return iter(queue.get, sentinel)

def _close_queue_when_done(
    queue_in: queue.Queue,
    queue_out: queue.Queue,
    sentinel: typing.Any = None,
):
    queue_in.join()
    queue_out.put(sentinel)

def _produce[T](
    producer: typing.Iterable[T],
    q: queue.Queue[T],
    task_done: typing.Callable[[], None],
):
    for res_it in producer:
        q.put(res_it)

    task_done()

def reduce_publishers[T](
    *publishers: typing.Iterable[T],
) -> typing.Generator[T]:
    queue_in = queue.Queue[typing.Iterable[T]]()
    queue_out = queue.Queue[T]()

    for publisher_it in publishers:
        queue_in.put(publisher_it)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(
            _close_queue_when_done,
            queue_in = queue_in,
            queue_out = queue_out,
        )

        while not queue_in.empty():
            executor.submit(
                _produce,
                queue_in.get(),
                queue_out,
                task_done = queue_in.task_done,
            )

        yield from to_iterator(queue_out)
