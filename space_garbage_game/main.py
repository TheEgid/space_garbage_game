import random
import curses
import asyncio
from itertools import cycle
import os
import sys

from physics import update_speed

from fire_animation import fire
from space_garbage import fly_garbage
from curses_tools import draw_frame
from curses_tools import get_frame_size
from curses_tools import read_controls

TIC_TIMEOUT = 0.1
STARS_SYMBOLS = '+*.:'
BORDER_SIZE = 2
coroutines = []
spaceship_frames_coroutines = []


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
        await random_sleep_delay(350)


def get_random_coordinates(canvas):
    x_max, y_max = canvas.getmaxyx()
    max_row, max_column = x_max - BORDER_SIZE, y_max - BORDER_SIZE
    _x = random.randint(BORDER_SIZE, max_row - BORDER_SIZE)
    _y = random.randint(BORDER_SIZE, max_column - BORDER_SIZE)
    return _x, _y


def calc_stars_amount(canvas, segment_ratio=50):
    x_max, y_max = canvas.getmaxyx()
    return (x_max * y_max) // segment_ratio


def make_blink_stars(canvas, stars_amount):
    for star in range(stars_amount):
        symbol = random.choice(STARS_SYMBOLS)
        row, column = get_random_coordinates(canvas=canvas)
        coroutines.append(blink_star(canvas, row, column, symbol))


async def animate_spaceship():
    global spaceship_frames_coroutines
    _frames = get_frame_from_file(r'rocket_frame_1.txt',
                                  r'rocket_frame_2.txt')
    for item in cycle(_frames):
        spaceship_frames_coroutines.clear()
        spaceship_frames_coroutines.append(item)
        await sleep_delay(20)


def make_fire(canvas, row, column):
    offset = 2
    coroutines.append(fire(canvas, row, column+offset, rows_speed=-0.007))


async def run_spaceship(canvas):
    frame_size_x, frame_size_y = get_frame_size(spaceship_frames_coroutines[0])
    row_max, column_max = canvas.getmaxyx()
    rocket_pos_row = (row_max * 0.5) - (frame_size_y // 2)
    rocket_pos_column = (column_max * 0.5) - (frame_size_x // 2)

    speed_row = speed_column = 0

    while True:
        for frame in spaceship_frames_coroutines:
            rows_direction, columns_direction, space_direction = read_controls(canvas)

            speed_row, speed_column = update_speed(speed_row, speed_column,
                                                   rows_direction, columns_direction)

            if BORDER_SIZE < (rocket_pos_row + speed_row) < \
                        (row_max - frame_size_x - BORDER_SIZE):
                rocket_pos_row += speed_row

            if BORDER_SIZE < (rocket_pos_column + speed_column) < \
                        (column_max - frame_size_y - BORDER_SIZE):
                rocket_pos_column += speed_column

            if space_direction:
                make_fire(canvas, rocket_pos_row, rocket_pos_column)

            draw_frame(canvas, rocket_pos_row, rocket_pos_column, frame)
            await sleep_delay(10)
            draw_frame(canvas, rocket_pos_row, rocket_pos_column, frame,
                           negative=True)


def coroutines_runner(canvas):
    while coroutines:
        for coroutine in coroutines:
            canvas.border()
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()


def game_process(canvas):
    global coroutines
    curses.initscr()
    curses.curs_set(0)
    curses.update_lines_cols()
    canvas.nodelay(True)

    stars_amount = calc_stars_amount(canvas)
    make_blink_stars(canvas, stars_amount)

    coroutines.append(animate_spaceship())

    coroutines.append(run_spaceship(canvas))

    coroutines.append(fill_orbit_with_garbage(canvas))

    coroutines_runner(canvas)



if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(game_process)
