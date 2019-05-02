
import random
import curses
import asyncio
import os
import sys

from fire_animation import fire
from curses_tools import draw_frame
from curses_tools import get_frame_size
from curses_tools import read_controls

TIC_TIMEOUT = 0.1
STARS_SYMBOLS = '+*.:'
BORDER_SIZE = 2


async def delay(tic):
    for cnt in range(int(tic // TIC_TIMEOUT)):
        await asyncio.sleep(0)


async def random_delay(min_delay=200, multiplic=10):
    delay = random.randint(min_delay, min_delay * multiplic)
    for cnt in range(delay):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    dim, normal, bold = curses.A_DIM, curses.A_NORMAL, curses.A_BOLD
    while True:
        canvas.addstr(row, column, symbol, dim)
        await random_delay()
        canvas.addstr(row, column, symbol, normal)
        await delay(30)
        canvas.addstr(row, column, symbol, bold)
        await delay(50)
        canvas.addstr(row, column, symbol, normal)
        await delay(30)


def get_random_coordinates(canvas):
    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - BORDER_SIZE, columns - BORDER_SIZE
    _x = random.randint(BORDER_SIZE, max_row - BORDER_SIZE)
    _y = random.randint(BORDER_SIZE, max_column - BORDER_SIZE)
    return _x, _y


def calc_stars_amount(canvas, segment_ratio=25):
    x_max, y_max = canvas.getmaxyx()
    return (x_max * y_max) // segment_ratio


def get_frames_from_files():
    frame_folder = r'frames'
    frame_file1 = os.path.join(frame_folder, r'rocket_frame_1.txt')
    frame_file2 = os.path.join(frame_folder, r'rocket_frame_2.txt')
    with open(frame_file1, "r") as f1:
        frame1 = f1.read()
    with open(frame_file2, "r") as f2:
        frame2 = f2.read()
    return frame1, frame2


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
            await delay(10)
            draw_frame(canvas, rocket_pos_row, rocket_pos_column, frame,
                       negative=True)


def make_blink_stars(canvas):
    curses.initscr()
    curses.curs_set(0)
    curses.update_lines_cols()

    canvas.nodelay(True)
    canvas.border()

    coroutines = []

    x, y = canvas.getmaxyx()
    start_row = x * 0.5
    start_column = y * 0.5

    stars_amount = calc_stars_amount(canvas=canvas)
    frames = get_frames_from_files()

    fire_offset = 2
    coroutines.append(rocket(canvas, start_row, start_column+fire_offset, frames))
    coroutines.append(
        fire(canvas, start_row , start_column ,
             rows_speed=-0.007))

    for star in range(stars_amount):
        symbol = random.choice(STARS_SYMBOLS)
        row, column = get_random_coordinates(canvas=canvas)
        coroutines.append(blink(canvas, row, column, symbol))

    while coroutines:
        for coroutine in coroutines:
            try:
                coroutine.send(None)  
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(make_blink_stars)
