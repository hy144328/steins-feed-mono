import asyncio
import collections.abc

async def batch_queue[T](
    queue: asyncio.Queue[T],
    batch_size: int,
) -> collections.abc.AsyncGenerator[list[T]]:
    batch_it: list[T] = []

    while True:
        try:
            item_it = await queue.get()
        except asyncio.QueueShutDown:
            if len(batch_it) > 0:
                yield batch_it

            break

        batch_it.append(item_it)

        if len(batch_it) == batch_size:
            yield batch_it
            batch_it = []
