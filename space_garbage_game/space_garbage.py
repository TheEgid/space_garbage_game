import asyncio
from curses_tools import draw_frame
from curses_tools import get_frame_size
from obstacles import Obstacle
from globals_vars import obstacles
from globals_vars import obstacles_in_last_collisions
from fire_animation import explode


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    row = 0
    column = max(column, 0)
    column = min(column, columns_number - 1)

    obstacle_width, obstacle_height = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, obstacle_width, obstacle_height)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row += speed
            if obstacle in obstacles_in_last_collisions:
                await explode(canvas, obstacle.row, obstacle.column)
                obstacles.remove(obstacle)
                obstacles_in_last_collisions.remove(obstacle)
                break
    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)

