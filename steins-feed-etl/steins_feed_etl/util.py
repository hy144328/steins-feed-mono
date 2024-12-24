import asyncio
import typing

async def batch_queue(
    q: asyncio.Queue,
    batch_size: int,
) -> typing.AsyncGenerator[list[typing.Any]]:
    batch_it = []

    while True:
        item_it = await q.get()

        if item_it is None:
            if len(batch_it) > 0:
                yield batch_it

            break

        batch_it.append(item_it)

        if len(batch_it) == batch_size:
            yield batch_it
            batch_it = []
