import asyncio
import curses
from curses_tools import draw_frame, get_frame_size
from globals_vars import obstacles_in_last_collisions, obstacles
from globals_vars import EXPLOSION_FRAMES
from services import get_frames_from_file, sleep_delay


async def explode(canvas, center_row, center_column):
    eframes1, eframes2, eframes3, eframes4 = EXPLOSION_FRAMES
    frames = get_frames_from_file(eframes1, eframes2, eframes3, eframes4)

    for frame in frames:
        draw_frame(canvas, center_row, center_column, frame)
        await sleep_delay(4)
        draw_frame(canvas, center_row, center_column, frame, negative=True)
        await sleep_delay(2)


async def fire(canvas, start_row, start_column, rows_speed=-0.3,
               columns_speed=0):
    row, column = start_row, start_column
    canvas.addstr(round(row), round(column), '*')

    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), 'O')

    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'
    rows, columns = canvas.getmaxyx()

    max_row, max_column = rows - 1, columns - 1
    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(column)):
                obstacles_in_last_collisions.append(obstacle)
