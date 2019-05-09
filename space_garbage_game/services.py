import asyncio
import random
import os

from globals_vars import FRAME_FOLDER
from globals_vars import TIC_TIMEOUT


async def sleep_delay(tics=1):
    for cnt in range(int(tics // TIC_TIMEOUT)):
        await asyncio.sleep(0)


async def random_sleep_delay(min_delay=200, multiply=10):
    delay = random.randint(min_delay, min_delay * multiply)
    for cnt in range(delay):
        await asyncio.sleep(0)


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


def get_frames_from_file(*args, frame_folder=FRAME_FOLDER):
    _frame = []
    for frame_file in args:
        filepath = os.path.join(frame_folder, frame_file)
        with open(filepath, "r") as _file:
            _frame.append(_file.read())
    return tuple(_frame)


