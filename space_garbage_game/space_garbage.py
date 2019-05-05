import asyncio

from curses_tools import draw_frame
from curses_tools import get_frame_size
from obstacles import Obstacle
from obstacles import show_obstacles

from globals_vars import coroutines
from globals_vars import obstacles


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    garbage_rows, garbage_columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, garbage_rows, garbage_columns)

    obstacles.append(obstacle)
    coroutines.append(show_obstacles(canvas, obstacles))

    try:
        while row < rows_number:

            draw_frame(canvas, row, column, garbage_frame)

            await asyncio.sleep(0)

            draw_frame(canvas, row, column, garbage_frame, negative=True)

            row += speed
            obstacle.row += speed

    finally:
        obstacles.remove(obstacle)
