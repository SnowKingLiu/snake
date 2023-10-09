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

    def supplement_food(self, food_num=1):
        plat = copy.deepcopy(self.plat)
        # Snake init coord
        plat[self.width // 2][self.height // 2] = -1
        for _ in range(food_num):
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

    def init_foods(self):
        if (
            self.food_num <= 0
            or self.food_num >= self.width * self.height - self.bomb_num
        ):
            raise Exception("food num is illegal.")
        self.supplement_food(self.food_num)

    def reset(self):
        # Clear the map
        self.plat[:] = PlatEnum.Ground.value
        # Initiate bombs
        self.init_bombs()
        # Initiate foods
        self.init_foods()

    def get_food_num(self):
        n = np.where(
            (PlatEnum.Food_SMALL.value == self.plat)
            | (PlatEnum.Food_MIDDLE.value == sb.plat.plat)
            | (PlatEnum.Food_LARGE.value == sb.plat.plat)
        )
        if not n:
            return 0
        return n[0].size


class Snake(object):
    def __init__(self, head):
        self.init_head = head
        self.head = copy.deepcopy(head)
        self.bodies = []
        self.score = []
        self.terminal = False

    def revive(self):
        self.score = []
        self.head = self.init_head
        self.bodies = []

    def over(self):
        self.terminal = True


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
        revive=False,
    ):
        self.width = width
        self.height = height
        self.food_scores = food_scores
        self.snake_num = snake_num
        self.snake_init_coord = [width // 2, height // 2]
        self.revive = revive
        self.snakes = {}
        self.food_score_map = self.init_score_map()
        self.score_food_map = {v: k for k, v in self.food_score_map.items()}
        self.food_num = food_num
        self.plat = Plat(
            width=width,
            height=height,
            food_num=food_num,
            max_food_total=max_food_total,
            score_map=self.food_score_map,
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
        self.snakes = {i: Snake(self.snake_init_coord) for i in range(self.snake_num)}
        # Reset args
        self.terminal = False

    def get_merge_snake_plat(self):
        plat = copy.deepcopy(self.plat.plat)
        for snake in self.snakes.values():
            head = snake.head
            plat[head[0]][head[1]] = PlatEnum.SnakeHead.value
            for body in snake.bodies:
                plat[body[0]][body[1]] = PlatEnum.SnakeBody.value
        return plat

    def get_next_item(self, snake_head_x, snake_head_y, direction):
        plat = self.get_merge_snake_plat()

        if direction == Direction.UP:
            if snake_head_x <= 0:
                return PlatEnum.Outside.value, None
            return (
                plat[snake_head_x - 1][snake_head_y],
                [snake_head_x - 1, snake_head_y],
            )

        elif direction == Direction.DOWN:
            if snake_head_x >= self.height - 1:
                return PlatEnum.Outside.value, None
            return (
                plat[snake_head_x + 1][snake_head_y],
                [snake_head_x + 1, snake_head_y],
            )

        elif direction == Direction.LEFT:
            if snake_head_y <= 0:
                return PlatEnum.Outside.value, None
            return (
                plat[snake_head_x][snake_head_y - 1],
                [snake_head_x, snake_head_y - 1],
            )

        elif direction == Direction.RIGHT:
            if snake_head_y >= self.width - 1:
                return PlatEnum.Outside.value, None
            return (
                plat[snake_head_x][snake_head_y + 1],
                [snake_head_x, snake_head_y + 1],
            )
        else:
            raise Exception(f"Unknown direct: {self.snake_direction}")

    @staticmethod
    def move(snake, next_coord, grown=False):
        snake.bodies.insert(0, snake.head)
        snake.head = next_coord
        if not grown:
            snake.bodies.pop()

    def drop_foods(self, snake):
        if not snake.bodies:
            return
        snake_list = [snake.head, *snake.bodies[:-1]]
        score = snake.score
        for i, body in enumerate(snake_list[: len(snake_list) // 2]):
            if self.plat.plat[body[0]][body[1]] == PlatEnum.Ground.value:
                self.plat.plat[body[0]][body[1]] = self.score_food_map[score[i]]

    def snake_move(self, snake_id, direction):
        if self.terminal:
            return
        if not self.snakes.get(snake_id):
            raise Exception("Unknown snake.")
        snake = self.snakes[snake_id]

        snake_head_x, snake_head_y = snake.head

        next_item, next_coord = self.get_next_item(
            snake_head_x, snake_head_y, direction
        )

        # The 1st joint
        if next_item == PlatEnum.SnakeBody.value and next_coord == snake.bodies[0]:
            # Ignore operation
            return

        # Food
        if next_item in (
            PlatEnum.Food_SMALL.value,
            PlatEnum.Food_MIDDLE.value,
            PlatEnum.Food_LARGE.value,
        ):
            snake.score.append(self.food_score_map[next_item])
            self.move(snake, next_coord, grown=True)
            self.plat.plat[next_coord[0]][next_coord[1]] = PlatEnum.Ground.value
            food_num = self.plat.get_food_num()
            if food_num < self.food_num:
                if not self.is_full():
                    self.plat.supplement_food()
            if food_num == 0:
                # Win
                self.terminal = True
                return

        # Snake body or Bomb or Outside
        elif next_item in [PlatEnum.Bomb.value, PlatEnum.Outside.value] or (
            next_item == PlatEnum.SnakeBody.value and next_coord != snake.bodies[-1]
        ):
            if self.revive:
                self.drop_foods(snake)
                snake.revive()
            else:
                snake.over()
                self.terminal = True
                return

        # Snake tail or Ground
        elif next_item == PlatEnum.Ground.value or (
            next_item == PlatEnum.SnakeBody.value and next_coord == snake.bodies[-1]
        ):
            self.move(snake, next_coord)

        # TODO
        self.print_plat()

    def print_plat(self):
        plat = self.get_merge_snake_plat()
        print(plat)

    def is_full(self):
        plat = self.get_merge_snake_plat()
        ground = np.where(plat == 0)
        if not ground:
            return True

        return ground[0].size <= 1

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
    sb = SnakeBase(width=5, height=5, bomb_num=5, food_num=5, revive=True)
    d = Direction.RIGHT
    for _ in range(10):
        sb.reset()
        sb.print_plat()
        sb.snake_move(0, d)
        # sb.print_plat()
        # while not sb.terminal:
        #     sb.run_a_turn()
        #     sb.print_plat()
