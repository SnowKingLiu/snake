# by:Snowkingliu
# 2023/10/8 09:41
from enum import Enum


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class PlatEnum(Enum):
    Outside = -1
    Ground = 0
    SnakeHead = 1
    SnakeBody = 2
    Bomb = 3
    Food_SMALL = 4
    Food_MIDDLE = 5
    Food_LARGE = 6
