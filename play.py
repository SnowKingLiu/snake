# by:Snowkingliu
# 2023/10/10 14:48
from games.snake_gui import SnakeCanvas


def main():
    sc = SnakeCanvas(
        width=15,
        height=10,
        bomb_num=15,
        food_num=5,
        revive=True,
        # Number of player(s)
        snake_num=2,
        # Screen size
        unit=15,
    )
    sc.start()


if __name__ == "__main__":
    main()
