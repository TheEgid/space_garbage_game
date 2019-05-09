import random
import curses
from itertools import cycle
import os
import sys
from globals_vars import coroutines, spaceship_frames_coroutines
from globals_vars import obstacles, year
from globals_vars import SPACESHIP_FRAMES, BORDER_SIZE, GAME_OVER_FRAME
from physics import update_speed
from fire_animation import fire
from space_garbage import fly_garbage
from curses_tools import read_controls, get_frame_size, draw_frame
from globals_vars import GARBAGE_FRAMES, STARS_SYMBOLS, PHRASES_DICT
from services import get_frames_from_file, sleep_delay, random_sleep_delay
from services import get_garbage_delay_tics


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


async def fill_orbit_with_garbage(canvas):
    global obstacles
    _, column_max = canvas.getmaxyx()
    offset = 7
    speed_correction = 0.001
    tics_correction = 500
    tics = get_garbage_delay_tics(year)
    while True:
        place = random.randint(1-offset, column_max-offset)
        speed = (random.randint(1, 3)) * speed_correction
        garbage_frame = random.choice(GARBAGE_FRAMES)
        garbage = get_frames_from_file(garbage_frame)[0]
        coroutines.append(fly_garbage(canvas, place, garbage, speed))

        if tics is not None:
            await sleep_delay(tics*tics_correction)
        else:
            await sleep_delay(tics_correction)


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
        await sleep_delay(20)


def make_fire(canvas, row, column):
    offset = 2
    coroutines.append(fire(canvas, row, column+offset, rows_speed=-0.007))


async def show_game_over(canvas):
    _frame = get_frames_from_file(GAME_OVER_FRAME[0])[0]
    row_max, column_max = canvas.getmaxyx()
    frame_size_x, frame_size_y = get_frame_size(_frame)
    row = row_max / 2 - frame_size_x / 2
    column = column_max / 2 - frame_size_y / 2
    while True:
        draw_frame(canvas, row, column, _frame)
        await sleep_delay(10)
        draw_frame(canvas, row, column, _frame, negative=True)


async def show_years(canvas):
    global year
    info_area = canvas.derwin(1, 1)
    phrase = ''
    while True:
        if PHRASES_DICT.get(year):
            phrase = PHRASES_DICT.get(year)
        msg = '{} {}'.format(year, phrase)
        draw_frame(info_area, 0, 0, msg)
        await sleep_delay(1000)
        year = year + 1
        draw_frame(info_area, 0, 0, msg, negative=True)


async def run_spaceship(canvas):
    frame_size_x, frame_size_y = get_frame_size(spaceship_frames_coroutines[0])
    row_max, column_max = canvas.getmaxyx()
    spaceship_pos_row = (row_max - frame_size_y) // 2
    spaceship_pos_column = (column_max - frame_size_x) // 2
    speed_row = speed_column = 0
    shooting_year = 2020

    while True:
        for frame in spaceship_frames_coroutines:
            rows_direction, columns_direction, \
                                        space_direction = read_controls(canvas)

            speed_row, speed_column = update_speed(speed_row,
                                                   speed_column,
                                                   rows_direction,
                                                   columns_direction)

            if BORDER_SIZE < (spaceship_pos_row + speed_row) < \
                        (row_max - frame_size_x - BORDER_SIZE):
                spaceship_pos_row += speed_row

            if BORDER_SIZE < (spaceship_pos_column + speed_column) < \
                        (column_max - frame_size_y - BORDER_SIZE):
                spaceship_pos_column += speed_column

            if space_direction and year >= shooting_year:
                make_fire(canvas, spaceship_pos_row, spaceship_pos_column)


            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column, frame)
            await sleep_delay(10)

            draw_frame(canvas, spaceship_pos_row, spaceship_pos_column, frame,
                           negative=True)

            for obstacle in obstacles:
                if obstacle.has_collision(spaceship_pos_row,
                                          spaceship_pos_column,
                                          frame_size_x,
                                          frame_size_y):
                    coroutines.append(show_game_over(canvas))
                    obstacles.remove(obstacle)
                    return None


def start_coroutines(canvas):
    curses.initscr()
    curses.curs_set(0)
    curses.update_lines_cols()
    canvas.nodelay(True)
    while coroutines:
        for coroutine in coroutines:
            canvas.border()
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()


def game_process(canvas):
    try:
        stars_amount = calc_stars_amount(canvas)
        make_blink_stars(canvas, stars_amount)

        coroutines.append(show_years(canvas))
        coroutines.append(animate_spaceship())
        coroutines.append(run_spaceship(canvas))
        coroutines.append(fill_orbit_with_garbage(canvas))

        start_coroutines(canvas)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    curses.wrapper(game_process)

