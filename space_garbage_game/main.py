import os
import time
import sys
import random
import curses
from itertools import cycle
import asyncio
from settings import TIC_TIMEOUT, SHOOTING_YEAR
from settings import PHRASES_DICT
from settings import GARBAGE_FRAMES, STARS_SYMBOLS
from settings import SPACESHIP_FRAMES, BORDER_SIZE, GAME_OVER_FRAME
from globals_vars import coroutines, spaceship_frames_coroutines
from globals_vars import obstacles, year
from physics import update_speed
from fire_animation import fire
from space_garbage import fly_garbage
from curses_tools import read_controls, get_frame_size, draw_frame
from services import get_frames_from_file, sleep_delay, random_sleep_delay
from services import get_garbage_delay_tics


async def blink_star(canvas, row, column, symbol='*'):
    dim, normal, bold = curses.A_DIM, curses.A_NORMAL, curses.A_BOLD
    while True:
        canvas.addstr(row, column, symbol, dim)
        await random_sleep_delay()
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(0.3)
        canvas.addstr(row, column, symbol, bold)
        await sleep_delay(0.5)
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(0.3)


async def fill_orbit_with_garbage(canvas):
    _, column_max = canvas.getmaxyx()
    offset = 7
    tics = get_garbage_delay_tics(year)
    while True:
        place = random.randint(1-offset, column_max-offset)
        speed = (random.randint(1, 3))
        garbage_frame = random.choice(GARBAGE_FRAMES)
        garbage = get_frames_from_file(garbage_frame)[0]
        coroutines.append(fly_garbage(canvas, place, garbage, speed))

        if tics is not None:
            await sleep_delay(tics)
        else:
            await sleep_delay(1)


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
        row, column = get_random_coordinates(canvas)
        coroutines.append(blink_star(canvas, row, column, symbol))


async def animate_spaceship():
    spaceship_frame1, spaceship_frame2 = SPACESHIP_FRAMES
    _frames = get_frames_from_file(spaceship_frame1, spaceship_frame2)
    for item in cycle(_frames):
        spaceship_frames_coroutines.clear()
        spaceship_frames_coroutines.append(item)
        await asyncio.sleep(0)


def make_fire(canvas, row, column):
    offset = 2
    coroutines.append(fire(canvas, row, column+offset, rows_speed=-3))


async def show_game_over(canvas):
    _frame = get_frames_from_file(GAME_OVER_FRAME[0])[0]
    row_max, column_max = canvas.getmaxyx()
    frame_size_x, frame_size_y = get_frame_size(_frame)
    row = row_max // 2 - frame_size_x // 2
    column = column_max // 2 - frame_size_y // 2
    while True:
        draw_frame(canvas, row, column, _frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, _frame, negative=True)


async def make_increment_years(canvas):
    global year
    info_area = canvas.derwin(1, 0, 0, 0)
    phrase = ''
    while True:
        if PHRASES_DICT.get(year):
            phrase = PHRASES_DICT.get(year)
        msg = '{} {}'.format(year, phrase)
        draw_frame(info_area, 0, 0, msg)
        await sleep_delay(1.5)
        info_area.refresh()
        year += 1
        draw_frame(info_area, 0, 0, msg, negative=True)


async def run_spaceship(canvas):
    frame_size_x, frame_size_y = get_frame_size(spaceship_frames_coroutines[0])
    row_max, column_max = canvas.getmaxyx()
    spaceship_pos_row = (row_max - frame_size_y) // 2
    spaceship_pos_column = (column_max - frame_size_x) // 2
    speed_row = speed_column = 0

    while True:
        for frame in spaceship_frames_coroutines:
            rows_direction, columns_direction, \
            space_direction = read_controls(canvas)

            speed_row, speed_column = update_speed(speed_row,
                                                   speed_column,
                                                   rows_direction,
                                                   columns_direction)

            spaceship_pos_row = min(row_max - frame_size_x - BORDER_SIZE,
                                    max(BORDER_SIZE,
                                        spaceship_pos_row + speed_row))
            spaceship_pos_column = min(column_max - frame_size_y - BORDER_SIZE,
                                       max(BORDER_SIZE,
                                           spaceship_pos_column + speed_column))

            if space_direction and year >= SHOOTING_YEAR:
                make_fire(canvas, spaceship_pos_row, spaceship_pos_column)

            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column, frame,
                       negative=True)

            for obstacle in obstacles:
                if obstacle.has_collision(spaceship_pos_row, spaceship_pos_column,
                                          frame_size_x, frame_size_y):
                    coroutines.append(show_game_over(canvas))
                    return False


def loop_coroutines(canvas):
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(0)
    canvas.nodelay(True)
    while coroutines:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
                canvas.border()
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)


def run_game_process(canvas):
    info_area = canvas.derwin(1, 1)
    try:
        stars_amount = calc_stars_amount(canvas)
        make_blink_stars(canvas, stars_amount)

        coroutines.append(make_increment_years(info_area))
        coroutines.append(animate_spaceship())
        coroutines.append(run_spaceship(canvas))
        coroutines.append(fill_orbit_with_garbage(canvas))
        loop_coroutines(canvas)
        
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(run_game_process)
