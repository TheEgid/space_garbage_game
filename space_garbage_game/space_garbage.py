import asyncio
import globals_vars
from curses_tools import draw_frame
from curses_tools import get_frame_size
from obstacles import Obstacle
from fire_animation import explode


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    row = 0
    column = max(column, 0)
    column = min(column, columns_number - 1)

    obstacle_width, obstacle_height = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, obstacle_width, obstacle_height)
    globals_vars.obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row += speed
            if obstacle in globals_vars.obstacles_in_last_collisions:
                await explode(canvas, obstacle.row, obstacle.column)
                globals_vars.obstacles.remove(obstacle)
                globals_vars.obstacles_in_last_collisions.remove(obstacle)
                break
    finally:
        if obstacle in globals_vars.obstacles:
            globals_vars.obstacles.remove(obstacle)

