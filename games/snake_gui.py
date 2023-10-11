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
        self.bind_keyboards()
        self.stop = False

        self.colors = [
            ("#4471D3", "#678CDB"),
            ("#1F9173", "#40C8A4"),
        ]
        self.cv_bombs = []
        self.cv_foods = {}
        self.cv_snakes = {}
        self.cv_headers = {}

    def snake_thread(self):
        while not self.stop:
            time.sleep(2000)

    def exit(self):
        self.stop = True
        self.canvas.destroy()
        self.canvas.quit()

    def reset_game(self):
        self.reset()
        self.update_map()

    def get_direction(self, keysym):
        directs_map = {
            "Up": [0, Direction.UP],
            "Down": [0, Direction.DOWN],
            "Left": [0, Direction.LEFT],
            "Right": [0, Direction.RIGHT],
            "w": [1, Direction.UP],
            "s": [1, Direction.DOWN],
            "a": [1, Direction.LEFT],
            "d": [1, Direction.RIGHT],
        }
        if keysym == "Escape":
            self.exit()
            return
        if keysym == "space":
            self.reset_game()
            return

        return directs_map.get(keysym, [None, None])

    def keyboards_press(self, event):
        snake_id, direction = self.get_direction(event.keysym)
        if snake_id is None:
            return
        self.snake_move(snake_id, direction)
        self.update_map()

    def bind_keyboards(self):
        self.canvas.bind_all("<Key>", self.keyboards_press)

    def build_ui(self):
        # Banner
        snakes = self.snakes

        self.cv_headers = {}
        for snake_id, snake in snakes.items():
            if len(snakes) > 1:
                text = f"Player {snake_id} score: {sum(snake.score)}"
            else:
                text = f"Score: {sum(snakes[0].score)}"
            self.cv_headers[snake_id] = self.canvas.create_text(
                self.canvas_width // 2,
                (3 + snake_id * 3) * self.unit,
                text=text,
                font=("HFSnakylines", 2 * self.unit),
                fill=self.colors[snake_id][0],
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

    def get_foods_coord(self):
        coords = np.where(
            (self.plat.plat == PlatEnum.Food_SMALL.value)
            | (self.plat.plat == PlatEnum.Food_MIDDLE.value)
            | (self.plat.plat == PlatEnum.Food_LARGE.value)
        )
        if not coords:
            return []

        return [
            [self.plat.plat[coords[0][i]][coords[1][i]], coords[0][i], coords[1][i]]
            for i in range(len(coords[0]))
        ]

    @staticmethod
    def get_coord_id(coord):
        return "_".join(map(str, coord))

    def update_map(self):
        # Food
        foods = self.get_foods_coord()
        food_coords = [self.get_coord_id(z[1:]) for z in foods]
        for food_coord_id, food_id in list(self.cv_foods.items()):
            if food_coord_id not in food_coords:
                self.canvas.delete(food_id)
                del self.cv_foods[food_coord_id]

        for food_size, x, y in foods:
            food_coord_id = self.get_coord_id([x, y])
            if food_coord_id in self.cv_foods:
                continue
            if food_size == PlatEnum.Food_SMALL.value:
                food_coord = self.get_absolute_coordinates(x, y)
                self.cv_foods[food_coord_id] = self.canvas.create_oval(
                    food_coord[0] + self.unit,
                    food_coord[1] + self.unit,
                    food_coord[2] - self.unit,
                    food_coord[3] - self.unit,
                    fill="#FFCF65",
                    outline="",
                )

            elif food_size == PlatEnum.Food_MIDDLE.value:
                food_coord = self.get_absolute_coordinates(x, y)
                self.cv_foods[food_coord_id] = self.canvas.create_oval(
                    food_coord[0] + 0.5 * self.unit,
                    food_coord[1] + 0.5 * self.unit,
                    food_coord[2] - 0.5 * self.unit,
                    food_coord[3] - 0.5 * self.unit,
                    fill="#EC8749",
                    outline="",
                )

            elif food_size == PlatEnum.Food_LARGE.value:
                food_coord = self.get_absolute_coordinates(x, y)
                self.cv_foods[food_coord_id] = self.canvas.create_oval(
                    food_coord[0],
                    food_coord[1],
                    food_coord[2],
                    food_coord[3],
                    fill="#F25D0B",
                    outline="",
                )

        # Snake
        for snake_id, snake in self.snakes.items():
            cv_snake = self.cv_snakes.get(snake_id)
            snake_head_coord = self.get_coord_id(snake.head)
            if not cv_snake:
                self.cv_snakes[snake_id] = {
                    "head": [
                        snake_head_coord,
                        self.canvas.create_rectangle(
                            *self.get_absolute_coordinates(*snake.head),
                            fill=self.colors[snake_id][0],
                            outline="",
                        ),
                    ],
                    "body": [],
                }
                cv_snake = self.cv_snakes[snake_id]
            # Head
            if cv_snake["head"][0] != snake_head_coord:
                x_now, y_now, _, _ = self.get_absolute_coordinates(
                    *map(int, cv_snake["head"][0].split("_"))
                )
                x, y, _, _ = self.get_absolute_coordinates(*snake.head)
                cv_snake["head"][0] = snake_head_coord
                self.canvas.move(cv_snake["head"][1], x - x_now, y - y_now)
            # Body
            snake_body_coords = [self.get_coord_id(c) for c in snake.bodies]
            cv_snake_body_map = {}
            for body_coord, body_id in cv_snake["body"]:
                if body_coord not in snake_body_coords:
                    self.canvas.delete(body_id)
                    continue
                cv_snake_body_map[body_coord] = [body_coord, body_id]
            cv_snake_body = []
            for body in snake.bodies:
                body_coord = self.get_coord_id(body)
                if body_coord not in cv_snake_body_map:
                    cv_snake_body.append(
                        [
                            body_coord,
                            self.canvas.create_rectangle(
                                *self.get_absolute_coordinates(*body),
                                fill=self.colors[snake_id][1],
                                outline="",
                            ),
                        ]
                    )
                else:
                    cv_snake_body.append(cv_snake_body_map[body_coord])
            cv_snake["body"] = cv_snake_body

            # Score
            self.canvas.delete(self.cv_headers[snake_id])
            if len(self.snakes) > 1:
                text = f"Player {snake_id} score: {sum(snake.score)}"
            else:
                text = f"Score: {sum(snakes[0].score)}"
            self.cv_headers[snake_id] = self.canvas.create_text(
                self.canvas_width // 2,
                (3 + snake_id * 3) * self.unit,
                text=text,
                font=("HFSnakylines", 2 * self.unit),
                fill=self.colors[snake_id][0],
            )

    def start(self):
        self.canvas.master.title("Snake")  # noqa

        self.reset()

        self.build_ui()
        self.init_envs()

        self.update_map()

        self.game_running.start()
        self.canvas.pack()
        self.canvas.mainloop()
        self.join()

    def get_absolute_coordinates(self, plat_x, plat_y):
        start_x = self.left_top[0] + 3 * plat_y * self.unit
        start_y = self.left_top[1] + 3 * plat_x * self.unit
        end_x = start_x + 3 * self.unit
        end_y = start_y + 3 * self.unit

        return start_x, start_y, end_x, end_y

    def init_envs(self):
        plat = self.plat.plat
        # Bombs
        bombs = np.where(plat == PlatEnum.Bomb.value)
        for i in range(bombs[0].size):
            bomb_coordinate = self.get_absolute_coordinates(bombs[0][i], bombs[1][i])
            self.cv_bombs.append(
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
        unit=15,
    )
    sc.start()
