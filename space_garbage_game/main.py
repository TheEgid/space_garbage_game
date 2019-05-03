
import random
import curses
import asyncio
import os
import sys

import physics

from fire_animation import fire
from space_garbage import fly_garbage
from curses_tools import draw_frame
from curses_tools import get_frame_size
from curses_tools import read_controls

TIC_TIMEOUT = 0.1
STARS_SYMBOLS = '+*.:'
BORDER_SIZE = 2
coroutines = []


def get_frame_from_file(*args, frame_folder=r'frames'):
    _frame = []
    for frame_file in args:
        filepath = os.path.join(frame_folder, frame_file)
        with open(filepath, "r") as _file:
            _frame.append(_file.read())
    return tuple(_frame)


async def sleep_delay(tics=1):
    for cnt in range(int(tics // TIC_TIMEOUT)):
        await asyncio.sleep(0)


async def random_sleep_delay(min_delay=200, multiplic=10):
    delay = random.randint(min_delay, min_delay * multiplic)
    for cnt in range(delay):
        await asyncio.sleep(0)


async def blink_star(canvas, row, column, symbol='*'):
    dim, normal, bold = curses.A_DIM, curses.A_NORMAL, curses.A_BOLD
    while True:
        canvas.addstr(row, column, symbol, dim)
        await random_sleep_delay()
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(30)
        canvas.addstr(row, column, symbol, bold)
        await sleep_delay(50)
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(30)


def get_random_garbage_frame():
    garbage_variants = [r'duck.txt', r'hubble.txt', r'lamp.txt',
                        r'trash_large.txt', r'trash_small.txt', r'trash_xl.txt']
    return random.choice(garbage_variants)


async def fill_orbit_with_garbage(canvas):
    _, column_max = canvas.getmaxyx()
    while True:
        place = random.randint(1, column_max-10)
        speed = (random.randint(4, 6)) * 0.001
        garbage_frame = get_random_garbage_frame()
        garbage = get_frame_from_file(garbage_frame, frame_folder=r'frames')[0]
        coroutines.append(fly_garbage(canvas, place, garbage, speed=speed))
        await sleep_delay(150)


def get_random_coordinates(canvas):
    x_max, y_max = canvas.getmaxyx()
    max_row, max_column = x_max - BORDER_SIZE, y_max - BORDER_SIZE
    _x = random.randint(BORDER_SIZE, max_row - BORDER_SIZE)
    _y = random.randint(BORDER_SIZE, max_column - BORDER_SIZE)
    return _x, _y


def calc_stars_amount(canvas, segment_ratio=25):
    x_max, y_max = canvas.getmaxyx()
    return (x_max * y_max) // segment_ratio


async def rocket(canvas, start_row, start_column, frames):
    current_frame = frames[0]
    rocket_size_x, rocket_size_y = get_frame_size(current_frame)
    row_max, column_max = canvas.getmaxyx()
    rocket_pos_column = start_column - rocket_size_x // 2
    rocket_pos_row = start_row - rocket_size_y // 2

    while True:
        for frame in frames:
            rows_direction, columns_direction, _ = read_controls(canvas)

            if BORDER_SIZE < (rocket_pos_row + rows_direction) < \
                    (row_max - rocket_size_x - BORDER_SIZE):
                rocket_pos_row += rows_direction

            if BORDER_SIZE < (rocket_pos_column + columns_direction) < \
                    (column_max - rocket_size_y - BORDER_SIZE):
                rocket_pos_column += columns_direction

            draw_frame(canvas, rocket_pos_row, rocket_pos_column, frame)
            await sleep_delay(10)
            draw_frame(canvas, rocket_pos_row, rocket_pos_column, frame,
                       negative=True)


def make_blink_stars(canvas, stars_amount):
    for star in range(stars_amount):
        symbol = random.choice(STARS_SYMBOLS)
        row, column = get_random_coordinates(canvas=canvas)
        coroutines.append(blink_star(canvas, row, column, symbol))


def game_process(canvas):
    curses.initscr()
    curses.curs_set(0)
    curses.update_lines_cols()
    canvas.nodelay(True)

    x_max, y_max = canvas.getmaxyx()
    start_row, start_column = x_max * 0.5, y_max * 0.5
    stars_amount = calc_stars_amount(canvas=canvas)
    make_blink_stars(canvas, stars_amount)

    rocket_frame = get_frame_from_file(r'rocket_frame_1.txt',
                                       r'rocket_frame_2.txt')

    fire_offset = 2
    coroutines.append(rocket(canvas, start_row, start_column+fire_offset, rocket_frame))

    coroutines.append(fire(canvas, start_row, start_column, rows_speed=-0.007))

    coroutines.append(fill_orbit_with_garbage(canvas))


    while coroutines:
        for coroutine in coroutines:
            canvas.border()
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(game_process)
