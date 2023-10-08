# by:Snowkingliu
# 2023/10/8 09:38
import copy
import random

import numpy as np
from libs.consts import Direction, PlatEnum


class Plat(object):
    def __init__(
        self,
        width=15,
        height=15,
        food_num=1,
        max_food_total=-1,
        score_map=None,
        bomb_num=0,
    ):
        if score_map is None:
            score_map = {PlatEnum.Food_MIDDLE.value: 1}
        self.score_map = score_map
        self.width = width
        self.height = height
        self.food_num = food_num
        self.bomb_num = bomb_num
        self.max_food_total = (
            max_food_total if max_food_total >= 0 else width * height - bomb_num - 1
        )
        self.plat = np.zeros([self.height, self.width], dtype=int)

    @staticmethod
    def get_random_ground(plat):
        empty_plat = np.where(plat == 0)
        # Full
        if not empty_plat[0].size:
            return []
        return random.choice([np.array(t).tolist() for t in np.nditer(empty_plat)])

    @staticmethod
    def is_all_ground_free(plat):
        copy_plat = copy.deepcopy(plat)
        ground_num = np.where(copy_plat <= 0)
        if not ground_num[0].size:
            return False
        start_point = random.choice(
            [np.array(t).tolist() for t in np.nditer(ground_num)]
        )
        spread_points = []

        def _spread(point):
            x = point[0]
            y = point[1]
            copy_plat[x][y] = -2
            free_num = 0
            # UP
            if x > 0 and copy_plat[x - 1][y] <= 0:
                free_num += 1
                if copy_plat[x - 1][y] != -2:
                    _spread([x - 1, y])
            # DOWN
            if x < copy_plat.shape[0] - 1 and copy_plat[x + 1][y] <= 0:
                free_num += 1
                if copy_plat[x + 1][y] != -2:
                    _spread([x + 1, y])
            # LEFT
            if y > 0 and copy_plat[x][y - 1] <= 0:
                free_num += 1
                if copy_plat[x][y - 1] != -2:
                    _spread([x, y - 1])
            # RIGHT
            if y < copy_plat.shape[1] - 1 and copy_plat[x][y + 1] <= 0:
                free_num += 1
                if copy_plat[x][y + 1] != -2:
                    _spread([x, y + 1])
            if free_num >= 2:
                spread_points.append(point)

        _spread(start_point)
        return len(spread_points) == ground_num[0].size

    def init_bombs(self):
        if self.bomb_num < 0 or self.bomb_num >= self.width * self.height:
            raise Exception("Bombs num is illegal.")
        plat = copy.deepcopy(self.plat)
        # Snake init coord
        plat[self.width // 2][self.height // 2] = -1
        remaining_bombs_num = self.bomb_num
        while remaining_bombs_num:
            point = self.get_random_ground(plat)
            if not point:
                raise Exception("The plat is too crowded")
            plat[point[0]][point[1]] = 1
            if self.is_all_ground_free(plat):
                remaining_bombs_num -= 1
                self.plat[point[0]][point[1]] = PlatEnum.Bomb.value
            else:
                plat[point[0]][point[1]] = -1

    def init_foods(self):
        if (
            self.food_num <= 0
            or self.food_num >= self.width * self.height - self.bomb_num
        ):
            raise Exception("food num is illegal.")
        plat = copy.deepcopy(self.plat)
        # Snake init coord
        plat[self.width // 2][self.height // 2] = -1
        for _ in range(self.food_num):
            if len(self.score_map) == 1:
                food = PlatEnum.Food_MIDDLE.value
            elif len(self.score_map) == 2:
                food = (
                    PlatEnum.Food_SMALL.value
                    if np.random.random() < 0.5
                    else PlatEnum.Food_MIDDLE.value
                )
            else:
                r = np.random.random()
                food = (
                    PlatEnum.Food_MIDDLE.value
                    if r < 0.66
                    else PlatEnum.Food_SMALL.value
                    if r < 0.83
                    else PlatEnum.Food_LARGE.value
                )
            point = self.get_random_ground(plat)
            if not point:
                raise Exception("The plat is too crowded")
            plat[point[0]][point[1]] = 1
            self.plat[point[0]][point[1]] = food

    def reset(self):
        # Clear the map
        self.plat[:] = PlatEnum.Ground.value
        # Initiate bombs
        self.init_bombs()
        # Initiate foods
        self.init_foods()


class Snake(object):
    def __init__(self, head):
        self.head = head
        self.bodies = []
        self.score = 0


class SnakeBase(object):
    def __init__(
        self,
        width=15,
        height=15,
        food_num=1,
        max_food_total=-1,
        food_scores=(1, 2, 3),
        bomb_num=0,
        snake_num=1,
    ):
        self.width = width
        self.height = height
        self.food_scores = food_scores
        self.snake_num = snake_num
        self.snakes = {}
        self.score_map = self.init_score_map()
        self.plat = Plat(
            width=width,
            height=height,
            food_num=food_num,
            max_food_total=max_food_total,
            score_map=self.score_map,
            bomb_num=bomb_num,
        )
        self.terminal = False

    def init_score_map(self):
        if len(self.food_scores) not in (1, 2, 3):
            raise Exception("Food scores is illegal.")

        if len(self.food_scores) == 1:
            return {PlatEnum.Food_MIDDLE.value: self.food_scores[0]}
        elif len(self.food_scores) == 2:
            return {
                [PlatEnum.Food_SMALL.value, PlatEnum.Food_MIDDLE.value][
                    i
                ]: self.food_scores[i]
                for i in range(len(self.food_scores))
            }
        else:
            return {
                [
                    PlatEnum.Food_SMALL.value,
                    PlatEnum.Food_MIDDLE.value,
                    PlatEnum.Food_LARGE.value,
                ][i]: self.food_scores[i]
                for i in range(len(self.food_scores))
            }

    def reset(self):
        # Reset plat
        self.plat.reset()

        # Reset snake
        for i in range(self.snake_num):
            if self.snakes.get(i):
                del self.snakes[i]
        self.snakes = {
            i: Snake([self.width // 2, self.height // 2]) for i in range(self.snake_num)
        }
        # Reset args
        self.terminal = False

    def get_next_item(self, snake_head_x, snake_head_y, direction):
        if direction == Direction.UP:
            if snake_head_x <= 0:
                return PlatEnum.Outside.value, None
            return (
                self.plat.plat[snake_head_x - 1][snake_head_y],
                [snake_head_x - 1, snake_head_y],
            )

        elif direction == Direction.DOWN:
            if snake_head_x >= self.height - 1:
                return PlatEnum.Outside.value, None
            return (
                self.plat.plat[snake_head_x + 1][snake_head_y],
                [snake_head_x + 1, snake_head_y],
            )

        elif direction == Direction.LEFT:
            if snake_head_y <= 0:
                return PlatEnum.Outside.value, None
            return (
                self.plat.plat[snake_head_x][snake_head_y - 1],
                [snake_head_x, snake_head_y - 1],
            )

        elif direction == Direction.RIGHT:
            if snake_head_y >= self.width - 1:
                return PlatEnum.Outside.value, None
            return (
                self.plat.plat[snake_head_x][snake_head_y + 1],
                [snake_head_x, snake_head_y + 1],
            )
        else:
            raise Exception(f"Unknown direct: {self.snake_direction}")

    def snake_move(self, snake_id, direction):
        if self.terminal:
            return
        if not self.snakes.get(snake_id):
            raise Exception("Unknown snake.")
        snake = self.snakes[snake_id]

        snake_head_x, snake_head_y = snake.head

        next_item, [next_head_x, next_head_y] = self.get_next_item(
            snake_head_x, snake_head_y, direction
        )
        # Food
        if next_item in (
            PlatEnum.Food_SMALL.value,
            PlatEnum.Food_MIDDLE.value,
            PlatEnum.Food_LARGE.value,
        ):
            snake.score += self.score_map[next_item]
            # self.move()
        # Snake body or Bomb

        # Snake tail or Ground

        next_coord = self.snake[0]
        for idx in range(1, len(self.snake)):
            current_coord = self.snake[idx]
            current_item = self.plat[current_coord[0]][current_coord[1]]
            self.plat[next_coord[0]][next_coord[1]] = current_item
            self.plat[current_coord[0]][current_coord[1]] = PlatEnum.Ground.value
            self.snake[idx] = next_coord
            next_coord = current_coord
        if self.plat[self.snake[0][0], self.snake[0][1]] == PlatEnum.SnakeHead.value:
            self.plat[self.snake[0][0], self.snake[0][1]] = PlatEnum.Ground.value
        self.plat[item_coord[0], item_coord[1]] = PlatEnum.SnakeHead.value
        self.snake[0] = item_coord

    def run_a_turn(self, snake_id, direction):
        if this.terminal:
            return
        if not self.snakes.get(snake_id):
            raise Exception("Unknown snake.")
        snake = self.snakes[snake_id]

        snake_head_x, snake_head_y = snake.head
        # next_item, item_coord = self.get_next_item(snake_head_x, snake_head_y)

        # Game over
        if next_item in [
            PlatEnum.Outside.value,
            PlatEnum.SnakeHead.value,
            PlatEnum.Bomb.value,
        ]:
            self.game_over()
            return next_item
        elif next_item == PlatEnum.SnakeBody.value:
            # The tail
            if item_coord == self.snake[-1]:
                self.snake_move(item_coord)
            else:
                self.game_over()
            return next_item
        # Eat food
        elif next_item == PlatEnum.Food.value:
            self.eat_food(item_coord)
            self.add_reward()
            self.score += 1

            # Add snake body
            body_coord = self.snake[-1]
            self.snake_move(item_coord)
            self.create_snake_body(body_coord)
            self.create_food()
            return next_item
        elif next_item == PlatEnum.Ground.value:
            self.snake_move(item_coord)
            new_distance = self.get_distance()
            de_reward = 0
            # if new_distance > distance:
            #     de_reward *= 2
            if new_distance < distance:
                de_reward = 0
            self.reduce_reward(value=de_reward)
            return next_item
        else:
            raise Exception(f"Unknown plat type. {next_item}")

    def eat_food(self, food_coord):
        self.plat[food_coord[0]][food_coord[1]] = PlatEnum.Ground.value
        self.foods.remove(food_coord)

    def create_snake_body(self, body_coord):
        self.plat[body_coord[0]][body_coord[1]] = PlatEnum.SnakeBody.value
        self.snake.append(body_coord)

    def get_distance(self):
        if self.food_num != 1:
            return 0
        return (self.foods[0][0] - self.snake[0][0]) ** 2 + (
            self.foods[0][1] - self.snake[0][1]
        ) ** 2

    def add_reward(self, value=1):
        self.reward += value

    def reduce_reward(self, value=1.0):
        self.reward -= value

    def print_plat(self):
        print(f"\n {self.plat}")
        print(f"Score: {self.score}, reward: {self.reward}")

    def set_direction(self, direction: Direction):
        if self.snake_direction == Direction.UP:
            if direction in [Direction.RIGHT, Direction.LEFT]:
                self.snake_direction = direction

        elif self.snake_direction == Direction.LEFT:
            if direction in [Direction.UP, Direction.DOWN]:
                self.snake_direction = direction

        elif self.snake_direction == Direction.RIGHT:
            if direction in [Direction.UP, Direction.DOWN]:
                self.snake_direction = direction

        elif self.snake_direction == Direction.DOWN:
            if direction in [Direction.RIGHT, Direction.LEFT]:
                self.snake_direction = direction
        else:
            raise Exception(f"Unknown direction. {direction}")

    @staticmethod
    def euclid_dis_sim(x, y):
        """
        欧几里得相似度
        :param x:
        :param y:
        :return:
        """
        return np.sqrt(np.sum((x - y) ** 2))

    def get_state(self):
        """
        0、地图
        :return:
        """
        return np.hstack(
            [self.plat.flatten(), self.get_action_by_direction(self.snake_direction)]
        )

    @staticmethod
    def get_direction_by_action(action: int) -> Direction:
        return [
            Direction.UP,
            Direction.LEFT,
            Direction.RIGHT,
            Direction.DOWN,
        ][action]

    @staticmethod
    def get_action_by_direction(direction: Direction) -> int:
        return [
            Direction.UP,
            Direction.LEFT,
            Direction.RIGHT,
            Direction.DOWN,
        ].index(direction)

    def do_action(self, direction: Direction):
        self.set_direction(direction)
        self.run_a_turn()
        return self.get_state()


if __name__ == "__main__":
    sb = SnakeBase(width=5, height=5, bomb_num=5, food_num=5)
    for _ in range(10):
        sb.reset()
        sb.snake_move(0, Direction.RIGHT)
        # sb.print_plat()
        # while not sb.terminal:
        #     sb.run_a_turn()
        #     sb.print_plat()
