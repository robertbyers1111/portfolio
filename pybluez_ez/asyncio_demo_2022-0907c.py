#!/usr/bin/env python3
"""
~~~~~~~~~~~~~
Using a Queue
~~~~~~~~~~~~~

From https://realpython.com/async-io-python/

The asyncio package provides queue classes that are designed to be similar to classes of the queue module. In our examples
so far, we haven’t really had a need for a queue structure. In chained.py, each task (future) is composed of a set of
coroutines that explicitly await each other and pass through a single input per chain.

There is an alternative structure that can also work with async IO: a number of producers, which are not associated with
each other, add items to a queue. Each producer may add multiple items to the queue at staggered, random, unannounced
times. A group of consumers pull items from the queue as they show up, greedily and without waiting for any other signal.

In this design, there is no chaining of any individual consumer to a producer. The consumers don’t know the number of
producers, or even the cumulative number of items that will be added to the queue, in advance.

It takes an individual producer or consumer a variable amount of time to put and extract items from the queue,
respectively. The queue serves as a throughput that can communicate with the producers and consumers without them talking
to each other directly.

Note: While queues are often used in threaded programs because of the thread-safety of queue.Queue(), you shouldn’t need to
concern yourself with thread safety when it comes to async IO. (The exception is when you’re combining the two, but that
isn’t done in this tutorial.)

One use-case for queues (as is the case here) is for the queue to act as a transmitter for producers and consumers that
aren’t otherwise directly chained or associated with each other.

The synchronous version of this program would look pretty dismal: a group of blocking producers serially add items to the
queue, one producer at a time. Only after all producers are done can the queue be processed, by one consumer at a time
processing item-by-item. There is a ton of latency in this design. Items may sit idly in the queue rather than be picked up
and processed immediately.

An asynchronous version, asyncq.py, is below. The challenging part of this workflow is that there needs to be a signal to
the consumers that production is done. Otherwise, await q.get() will hang indefinitely, because the queue will have been
fully processed, but consumers won’t have any idea that production is complete.

(Big thanks for some help from a StackOverflow user for helping to straighten out main(): the key is to await q.join(),
which blocks until all items in the queue have been received and processed, and then to cancel the consumer tasks, which
would otherwise hang up and wait endlessly for additional queue items to appear.)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first few coroutines are helper functions that return a random string, a fractional-second performance counter, and a
random integer. A producer puts anywhere from 1 to 5 items into the queue. Each item is a tuple of (i, t) where i is a
random string and t is the time at which the producer attempts to put the tuple into the queue.

When a consumer pulls an item out, it simply calculates the elapsed time that the item sat in the queue using the timestamp
that the item was put in with.

Keep in mind that asyncio.sleep() is used to mimic some other, more complex coroutine that would eat up time and block all
other execution if it were a regular blocking function.

Here is a test run with two producers and five consumers:

$ python3 asyncq.py -p 2 -c 5
Producer 0 sleeping for 3 seconds.
Producer 1 sleeping for 3 seconds.
Consumer 0 sleeping for 4 seconds.
Consumer 1 sleeping for 3 seconds.
Consumer 2 sleeping for 3 seconds.
Consumer 3 sleeping for 5 seconds.
Consumer 4 sleeping for 4 seconds.
Producer 0 added <377b1e8f82> to queue.
Producer 0 sleeping for 5 seconds.
Producer 1 added <413b8802f8> to queue.
Consumer 1 got element <377b1e8f82> in 0.00013 seconds.
Consumer 1 sleeping for 3 seconds.
Consumer 2 got element <413b8802f8> in 0.00009 seconds.
Consumer 2 sleeping for 4 seconds.
Producer 0 added <06c055b3ab> to queue.
Producer 0 sleeping for 1 seconds.
Consumer 0 got element <06c055b3ab> in 0.00021 seconds.
Consumer 0 sleeping for 4 seconds.
Producer 0 added <17a8613276> to queue.
Consumer 4 got element <17a8613276> in 0.00022 seconds.
Consumer 4 sleeping for 5 seconds.
Program completed in 9.00954 seconds.

In this case, the items process in fractions of a second. A delay can be due to two reasons:

    Standard, largely unavoidable overhead
    Situations where all consumers are sleeping when an item appears in the queue

With regards to the second reason, luckily, it is perfectly normal to scale to hundreds or thousands of consumers. You
should have no problem with python3 asyncq.py -p 5 -c 100. The point here is that, theoretically, you could have different
users on different systems controlling the management of producers and consumers, with the queue serving as the central
throughput.
"""

import asyncio
import itertools as it
import os
import random
import time
from datetime import datetime


def print_msg(msg):
    t = datetime.now().strftime('%Y-%m%d-%H:%M:%S.%f')
    print(f"{t} {msg}")


async def make_item(size: int = 5) -> str:
    return os.urandom(size).hex()


async def rand_sleep(caller=None) -> None:
    i = random.randint(0, 10)
    if caller:
        print_msg(f"{caller} sleeping for {i} seconds.")
    await asyncio.sleep(i)


async def produce(name: int, q: asyncio.Queue) -> None:
    n = random.randint(0, 10)
    for _ in it.repeat(None, n):  # Synchronous loop for each single producer
        await rand_sleep(caller=f"Producer {name}")
        i = await make_item()
        t = time.perf_counter()
        await q.put((i, t))
        print_msg(f"Producer {name} added <{i}> to queue.")


async def consume(name: int, q: asyncio.Queue) -> None:
    while True:
        await rand_sleep(caller=f"Consumer {name}")
        i, t = await q.get()
        now = time.perf_counter()
        print_msg(f"Consumer {name} got element <{i}> in {now-t:0.5f} seconds.")
        q.task_done()


async def main(n_prod: int, ncon: int):
    q = asyncio.Queue()
    producers = [asyncio.create_task(produce(n, q)) for n in range(n_prod)]
    consumers = [asyncio.create_task(consume(n, q)) for n in range(ncon)]
    await asyncio.gather(*producers)
    await q.join()  # Implicitly awaits consumers, too
    for c in consumers:
        c.cancel()

if __name__ == "__main__":
    import argparse
    random.seed(444)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--n_prod", type=int, default=5)
    parser.add_argument("-c", "--ncon", type=int, default=10)
    ns = parser.parse_args()
    start = time.perf_counter()
    asyncio.run(main(**ns.__dict__))
    elapsed = time.perf_counter() - start
    print_msg(f"Program completed in {elapsed:0.5f} seconds.")
