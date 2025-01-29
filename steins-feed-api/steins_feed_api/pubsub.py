import concurrent.futures
import queue
import typing

def to_iterator[T](
    queue: queue.Queue[T],
    sentinel: typing.Any = None,
) -> typing.Iterator[T]:
    return iter(queue.get, sentinel)

def to_queue[T](
    result: typing.Iterable[T],
    sentinel: typing.Any = None,
) -> queue.Queue[T]:
    q = queue.Queue[T]()

    for res_it in result:
        q.put(res_it)

    q.put(sentinel)
    return q

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
    queue_in = to_queue(publishers)
    queue_out = queue.Queue[T]()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(
            _close_queue_when_done,
            queue_in = queue_in,
            queue_out = queue_out,
        )

        for producer_it in to_iterator(queue_in):
            executor.submit(
                _produce,
                producer_it,
                queue_out,
                task_done = queue_in.task_done,
            )

        yield from to_iterator(queue_out)
