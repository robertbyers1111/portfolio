#!/usr/bin/env python3
"""
From https://realpython.com/async-io-python/

Here’s one example of how async IO cuts down on wait time: given a coroutine make_random() that keeps producing random integers
in the range [0, 100], until one of them exceeds a threshold, you want to let multiple calls of this coroutine not need to wait
for each other to complete in succession.

"""

import asyncio
import random
import datetime
from datetime import datetime

# ANSI colors
c = (
    "\033[0m",   # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)


def print_msg(idx, msg):
    t = datetime.now().strftime('%S.%f')
    print(c[idx + 1] + f"{t} {msg}")


async def make_random(idx: int, threshold: int = 67) -> int:
    print_msg(idx, f"Initiated make_random({idx}) with threshold {threshold}.")
    val = random.randint(0, 100)
    while val <= threshold:
        print_msg(idx, f"id {idx} selected {val}, which is less than {threshold}. id {idx} is now ceding control to others for {3*(idx+1)} seconds..")
        await asyncio.sleep(3*(idx + 1))
        val = random.randint(0, 100)
    print_msg(idx, f"---> FINISHED: make_random({idx}) == {val} (threshold {threshold})" + c[0] + '\n')
    return val


async def main():
    res = await asyncio.gather(*(make_random(i, 100 - i - 2) for i in range(3)))
    return res

if __name__ == "__main__":
    ran_seed = datetime.now().strftime("%f")
    print(f"random seed: {ran_seed}\n")
    random.seed(ran_seed)
    r1, r2, r3 = asyncio.run(main())
    print(f"\nr1: {r1}, r2: {r2}, r3: {r3}")
