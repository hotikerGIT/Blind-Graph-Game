import random
from values import *


class GraphMap:
    """
    Класс, отвечающий за карту игры, имеющий вид
    графа, состоящего из вершин и ребер
    """

    def __init__(self, spots_amount: int):
        """
        Инициализатор карты, принимающий количество вершин, после чего
        создающий случайное количество ребер, соединяющих
        данные вершины
        :param spots_amount: Количество вершин на карте
        """

        self.spots_amount = spots_amount

        # Атрибут, отвечающий за хранение информации о вершинах
        # является словарем, содержащим класс Вершин
        self.graph = {}

        for spot_name in range(1, spots_amount + 1):
            new_spot = Spot(spot_name)

    def add_spot(self, spot: 'Spot') -> None:
        pass


class Spot:
    """
    Класс, отвечающий за хранение информации о
    конкретной вершине графа.
    Содержит название вершины и информацию о ребрах,
    которые соединяют данную вершину с другой
    """

    def __init__(self, spot_name: int):
        """
        Инициализация точки, принимающая ее имя в качестве
        целого числа и создающая матрицу смежности для заданной точки
        :param spot_name: Числовое имя вершины
        """

        self.spot_name = spot_name
        self.directions = ([0, 0, 0],
                           [0, spot_name, 0],
                           [0, 0, 0])

    def add_edge(self, other: 'Spot', direction: str) -> bool:
        """
        Функция добавления ребра для графа.
        Принимает две вершины, после чего проверяет, свободно ли направление
        для обеих точек, затем добавляет связь между ними
        :param other: Другая вершина графа
        :param direction: строковая команда направления
        :return: удалось ли добавить ребро
        """

        # Получаем индексы для каждого направления
        x1, y1 = DIRECTION_ASSIGNMENT[direction]
        x2, y2 = DIRECTION_ASSIGNMENT[get_reverse_direction(direction)]

        # Если для вершины можно провести ребро, то мы его проводим
        if (
            self.directions[x1][y1] == 0 and
            other.directions[x2][y2] == 0
        ):
            self.directions[x1][y1] = other.spot_name
            other.directions[x2][y2] = self.spot_name
            return True

        return False

    def get_free_directions(self) -> list[str]:
        """
        Функция, возвращающая список строковых команд
        для направлений, которые еще не заняты вершинами
        :return:
        """

        res = []

        for row_index, row in enumerate(self.directions):
            for col_index, col in enumerate(row):
                if col == 0:
                    res.append(DIRECTIONS[row_index * 3 + col_index])

        return res