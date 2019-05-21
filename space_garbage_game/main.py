import os
import time
import sys
import random
import curses
from itertools import cycle
import asyncio
import globals_vars
from settings import TIC_TIMEOUT, SHOOTING_YEAR, OCCURRENCE_GARBAGE_YEAR
from settings import PHRASES_DICT, GARBAGE_FRAMES, STARS_SYMBOLS
from settings import SPACESHIP_FRAMES, BORDER_SIZE, GAME_OVER_FRAME
from physics import update_speed
from fire_animation import fire
from space_garbage import fly_garbage
from curses_tools import read_controls, get_frame_size, draw_frame
from services import get_frames_from_file, sleep_delay
from services import get_garbage_delay_tics


async def blink_star(canvas, row, column, symbol, offset_tics):
    dim, normal, bold = curses.A_DIM, curses.A_NORMAL, curses.A_BOLD
    while True:
        canvas.addstr(row, column, symbol, dim)
        await sleep_delay(TIC_TIMEOUT * offset_tics)
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(TIC_TIMEOUT * 3)
        canvas.addstr(row, column, symbol, bold)
        await sleep_delay(TIC_TIMEOUT * 5)
        canvas.addstr(row, column, symbol, normal)
        await sleep_delay(TIC_TIMEOUT * 3)


async def fill_orbit_with_garbage(canvas):
    _, columns_number = canvas.getmaxyx()
    offset = 7
    while True:
        tics = get_garbage_delay_tics(globals_vars.year)
        place = random.randint(1-offset, columns_number-offset)
        speed = random.randint(1, 3)
        garbage_frame = random.choice(GARBAGE_FRAMES)
        garbage = get_frames_from_file(garbage_frame)[0]
        if globals_vars.year >= OCCURRENCE_GARBAGE_YEAR:
            globals_vars.coroutines.append(fly_garbage(canvas, place, garbage, speed))

        if tics is not None:
            await sleep_delay(tics*TIC_TIMEOUT)
        else:
            await sleep_delay(1)


def get_random_coordinates(canvas):
    rows_number, columns_number = canvas.getmaxyx()
    max_x, max_y = rows_number - BORDER_SIZE, columns_number - BORDER_SIZE
    _x = random.randint(BORDER_SIZE, max_x - BORDER_SIZE)
    _y = random.randint(BORDER_SIZE, max_y - BORDER_SIZE)
    return _x, _y


def calc_stars_amount(canvas, segment_ratio=50):
    rows_number, columns_number = canvas.getmaxyx()
    return (rows_number * columns_number) // segment_ratio


def make_blink_stars(canvas, stars_amount, tics=5):
    for star in range(stars_amount):
        row, column = get_random_coordinates(canvas)
        symbol = random.choice(STARS_SYMBOLS)
        offset_tics = random.randint(tics//tics, tics*tics)
        globals_vars.coroutines.append(blink_star(canvas, row, column, symbol, offset_tics))


def make_fire(canvas, row, column):
    offset = 2
    globals_vars.coroutines.append(fire(canvas, row, column+offset, rows_speed=-3))


async def show_game_over(canvas):
    _frame = get_frames_from_file(GAME_OVER_FRAME[0])[0]
    rows_number, columns_number = canvas.getmaxyx()
    frame_size_x, frame_size_y = get_frame_size(_frame)
    row = rows_number // 2 - frame_size_x // 2
    column = columns_number // 2 - frame_size_y // 2
    while True:
        draw_frame(canvas, row, column, _frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, _frame, negative=True)


async def make_increment_years(canvas):
    info_area = canvas.derwin(1, 0, 0, 0)
    phrase = ''
    while True:
        if PHRASES_DICT.get(globals_vars.year):
            phrase = PHRASES_DICT.get(globals_vars.year)
        msg = '{} {}'.format(globals_vars.year, phrase)
        draw_frame(info_area, 0, 0, msg)
        await sleep_delay(1.5)
        info_area.refresh()
        globals_vars.year += 1
        draw_frame(info_area, 0, 0, msg, negative=True)


async def run_spaceship(canvas):
    spaceship_frames = get_frames_from_file(*SPACESHIP_FRAMES)
    frame_size_x, frame_size_y = get_frame_size(spaceship_frames[0])

    rows_number, columns_number = canvas.getmaxyx()
    spaceship_pos_row = (rows_number - frame_size_y) // 2
    spaceship_pos_column = (columns_number - frame_size_x) // 2
    speed_row = speed_column = 0

    while True:
        for spaceship_frame in cycle(spaceship_frames):
            rows_direction, columns_direction, \
            space_direction = read_controls(canvas)

            speed_row, speed_column = update_speed(speed_row,
                                                   speed_column,
                                                   rows_direction,
                                                   columns_direction)

            position_max_row = rows_number - frame_size_x - BORDER_SIZE
            position_min_row = spaceship_pos_row + speed_row
            position_max_column = columns_number - frame_size_y - BORDER_SIZE
            position_min_column = spaceship_pos_column + speed_column

            spaceship_pos_row = min(position_max_row,
                                    max(BORDER_SIZE, position_min_row))
            spaceship_pos_column = min(position_max_column,
                                       max(BORDER_SIZE, position_min_column))

            if space_direction and globals_vars.year >= SHOOTING_YEAR:
                make_fire(canvas, spaceship_pos_row, spaceship_pos_column)

            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column,
                       spaceship_frame)

            await asyncio.sleep(0)

            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column,
                       spaceship_frame, negative=True)

            for obstacle in globals_vars.obstacles:
                if obstacle.has_collision(spaceship_pos_row, spaceship_pos_column,
                                          frame_size_x, frame_size_y):
                    globals_vars.coroutines.append(show_game_over(canvas))
                    return False


def loop_coroutines(canvas):
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(0)
    canvas.nodelay(True)
    while globals_vars.coroutines:
        for coroutine in globals_vars.coroutines:
            try:
                coroutine.send(None)
                canvas.border()
            except StopIteration:
                globals_vars.coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)



def run_game_process(canvas):
    info_area = canvas.derwin(1, 1)
    try:
        stars_amount = calc_stars_amount(canvas)
        make_blink_stars(canvas, stars_amount)
        globals_vars.coroutines.append(make_increment_years(info_area))
        globals_vars.coroutines.append(run_spaceship(canvas))
        globals_vars.coroutines.append(fill_orbit_with_garbage(canvas))
        loop_coroutines(canvas)
        
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(run_game_process)
