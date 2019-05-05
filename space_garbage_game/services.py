import asyncio
import random
import os

from globals_vars import FRAME_FOLDER
from globals_vars import TIC_TIMEOUT


def get_frames_from_file(*args, frame_folder=FRAME_FOLDER):
    _frame = []
    for frame_file in args:
        filepath = os.path.join(frame_folder, frame_file)
        with open(filepath, "r") as _file:
            _frame.append(_file.read())
    return tuple(_frame)


async def sleep_delay(tics=1):
    for cnt in range(int(tics // TIC_TIMEOUT)):
        await asyncio.sleep(0)


async def random_sleep_delay(min_delay=200, multiply=10):
    delay = random.randint(min_delay, min_delay * multiply)
    for cnt in range(delay):
        await asyncio.sleep(0)