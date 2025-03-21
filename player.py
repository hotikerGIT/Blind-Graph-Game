from items import Item
from map_generating import *


class Player:
    """
    Класс, отвечающий за игроков на карте.
    Должен давать возможность перемещаться, хранить данные,
    индицировать конец игры.
    """

    def __init__(self, starting_position: 'Spot'):
        # Хранение инвентаря
        self.gold = 0
        self.items: list[Item] = []

        # Индикаторы окончания игры
        self.score = 0
        self.lives = 3

        # Перемещение персонажа
        self.position: 'Spot' = starting_position

        # Прячется или догоняет
        self.is_hiding = True

    def indicate_directions(self) -> list[bool]:
        res = []

        for row in self.position.directions:
            for directions in row:
                res.append(directions != -1 and directions)

        return res

    def move(self, direction: tuple[int, int]) -> None:
        self.position = self.position.directions[direction[0]][direction[1]]