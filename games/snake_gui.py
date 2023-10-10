# by:Snowkingliu
# 2023/10/10 14:50
from tkinter import Canvas
import threading
import time

import numpy as np

from snake_base import SnakeBase
from libs.consts import Direction, PlatEnum


class SnakeCanvas(SnakeBase):
    def __init__(
        self,
        width=20,
        height=15,
        bomb_num=10,
        food_num=5,
        snake_num=2,
        revive=True,
        unit=5,
        auto_run=False,
    ):
        self.unit = unit
        super().__init__(
            width=width,
            height=height,
            food_num=food_num,
            bomb_num=bomb_num,
            revive=revive,
            snake_num=snake_num,
        )
        self.auto_run = auto_run

        self.head_height = (2 + snake_num * 3) * self.unit
        self.canvas_width = max(250, (2 + 3 * width) * unit)
        self.canvas_height = self.head_height + (3 * height + 1) * unit
        self.canvas = Canvas(
            width=self.canvas_width,
            height=self.canvas_height,
            background="white",
        )

        self.left_base = (
            unit + 3
            if (2 + 3 * width) * unit >= 250
            else (250 - 3 * width * unit) // 2 + 3
        )
        self.left_top = [self.left_base, self.head_height]
        self.right_top = [self.left_base + 3 * width * unit, self.head_height]
        self.left_bottom = [self.left_base, self.head_height + 3 * height * unit]
        self.right_bottom = [
            self.left_base + 3 * width * unit,
            self.head_height + 3 * height * unit,
        ]

        self.game_running = threading.Thread(target=self.snake_thread)
        self.stop = False
        self.bombs = []
        self.header_ids = None

    def snake_thread(self):
        while not self.stop:
            time.sleep(2000)

    def keyboards_press(self, event):
        ...

    def bind_keyboards(self):
        self.canvas.bind_all("<Key>", self.keyboards_press)

    def build_ui(self):
        colors = [
            ("#4471D3", "#678CDB"),
            ("#1F9173", "#40C8A4"),
            ("#4471D3", "#678CDB"),
            ("#1F9173", "#40C8A4"),
            ("#4471D3", "#678CDB"),
            ("#1F9173", "#40C8A4"),
        ]

        # Banner
        snakes = self.snakes

        self.header_ids = {}
        for snake_id, snake in snakes.items():
            if len(snakes) > 1:
                text = f"Player {snake_id} score: {sum(snake.score)}"
            else:
                text = f"Score: {sum(snakes[0].score)}"
            self.header_ids[snake_id] = self.canvas.create_text(
                self.canvas_width // 2,
                (3 + snake_id * 3) * self.unit,
                text=text,
                font=("HFSnakylines", 2 * self.unit),
                fill=colors[snake_id][0],
            )

        line_colour = "#2B0B87"

        self.canvas.create_rectangle(
            self.left_top[0] - 1,
            self.left_top[1] - 1,
            self.right_top[0] + 1,
            self.right_top[1] - 1,
            fill=line_colour,
            outline="",
        )
        self.canvas.create_rectangle(
            self.left_top[0] - 1,
            self.left_top[1] - 1,
            self.left_bottom[0] - 1,
            self.left_bottom[1] + 1,
            fill=line_colour,
            outline="",
        )
        self.canvas.create_rectangle(
            self.right_top[0] + 1,
            self.right_top[1] - 1,
            self.right_bottom[0] + 1,
            self.right_bottom[1] + 1,
            fill=line_colour,
            outline="",
        )
        self.canvas.create_rectangle(
            self.left_bottom[0] - 1,
            self.left_bottom[1] + 1,
            self.right_bottom[0] + 1,
            self.right_bottom[1] + 1,
            fill=line_colour,
            outline="",
        )
        # self.replace_title()

    def start(self):
        self.canvas.master.title("Snake")  # noqa

        self.reset()

        self.build_ui()
        self.init_envs()

        self.game_running.start()
        self.canvas.pack()
        self.canvas.mainloop()
        self.join()

    def get_absolute_coordinates(self, plat_x, plat_y):
        start_x = self.left_top[0] + 3 * plat_x * self.unit
        start_y = self.left_top[1] + 3 * plat_y * self.unit
        end_x = start_x + 3 * self.unit
        end_y = start_y + 3 * self.unit

        return start_x, start_y, end_x, end_y

    def init_envs(self):
        plat = self.plat.plat
        # Bombs
        bombs = np.where(plat == PlatEnum.Bomb.value)
        for i in range(bombs[0].size):
            bomb_coordinate = self.get_absolute_coordinates(bombs[1][i], bombs[0][i])
            self.bombs.append(
                self.canvas.create_rectangle(
                    *bomb_coordinate, fill="#6C6C6C", outline=""
                )
            )

    def join(self):
        self.game_running.join()


if __name__ == "__main__":
    sc = SnakeCanvas(
        width=15,
        height=10,
        bomb_num=15,
        food_num=5,
        revive=True,
        snake_num=2,
        auto_run=False,
        unit=5,
    )
    sc.start()
