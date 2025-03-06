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
        self.graph: dict[int, tuple['Spot', tuple[int, int]]] = {1: (Spot(1), (spots_amount, spots_amount))}

        # Атрибут, отвечающий за отображение карты
        self.matrix: list[list[int]] = [
            [0 for _ in range(spots_amount * 2 + 1)]
            for _ in range(spots_amount * 2 + 1)
        ]
        self.matrix[spots_amount][spots_amount] = 1

        for spot_name in range(2, spots_amount + 1):
            new_spot = Spot(spot_name)
            self.add_spot(new_spot)

    def add_spot(self, spot: 'Spot') -> None:
        toggle = False

        while not toggle:
            connection, cords = random.choice(list(self.graph.values()))

            free_directions = connection.get_free_directions()
            if not free_directions:
                continue

            picked_direction: str = random.choice(free_directions)

            pick: tuple[int, int] = DIRECTION_ASSIGNMENT[picked_direction]
            attach: tuple[int, int] = DIRECTION_ASSIGNMENT[DIRECTION_OPPOSITES[picked_direction]]
            new_x, new_y = cords[0] + pick[0] - 1, cords[1] + pick[1] - 1

            if self.matrix[new_x][new_y]:
                continue

            spot.directions[attach[0]][attach[1]] = connection.spot_name
            connection.directions[pick[0]][pick[1]] = spot.spot_name

            self.matrix[new_x][new_y] = spot.spot_name
            self.graph[spot.spot_name] = (spot, (new_x, new_y))

            # Просматриваем точки, находящиеся в 1 шаге от нашей
            close_points: list[tuple['Spot', tuple[int, int]]] = []
            for x, y in DIRECTION_ASSIGNMENT.values():
                spot_cords = new_x - x - 1, new_y - y - 1
                content = self.matrix[spot_cords[0]][spot_cords[1]]

                if content:
                    close_points.append((self.graph[content][0], (x, y)))

            # Выбираем несколько точек, которые находятся вблизи с данной, и связываем их ребрами
            for _ in range(random.randint(0, random.choice(EDGE_COUNT_CHANCES))):
                if close_points:
                    random_pick = random.choice(close_points)
                    new_spot, (x, y) = random_pick
                    close_points.remove(random_pick)

                    spot.directions[x][y] = new_spot.spot_name
                    new_spot.directions[2 - x][2 - x] = spot.spot_name

            toggle = True

    def disallow_intersections(self, spot: 'Spot') -> None:
        """
        Функция, которая убирает возможность создания пересечений ребер
        за счет занимания места в том случае, если добавление ребра
        в каком-то направлении неизбежно приводит к созданию пересечения.
        Например:
        1 0
        1 1
        в данном примере у левой нижней вершины создание ребра вправо-вверх
        приведет к пересечению
        :param spot: вершина, которую нужно ограничить
        :return:
        """

        used_directions = {}

        for row_index, row in enumerate(spot.directions):
            for col_index, col in enumerate(row):
                if spot.directions[row_index][col_index] != 0:
                    string_direction = DIRECTIONS[row_index * 3 + col_index]
                    spot_name = spot.directions[row_index][col_index]

                    used_directions[string_direction] = spot_name

        if 'up' in used_directions.keys():
            for direction, spot_name in used_directions.items():
                check_point: 'Spot' = self.graph[spot_name][0]
                if direction == 'left' and check_point.check_connection('up-right'):
                    spot.directions[0][2] = -1

                if direction == 'right' and check_point.check_connection('up-left'):
                    spot.directions[0][0] = -1

        if 'down' in used_directions.keys():
            for direction, spot_name in used_directions.items():
                check_point: 'Spot' = self.graph[spot_name][0]
                if direction == 'left' and check_point.check_connection('down-right'):
                    spot.directions[2][2] = -1

                if direction == 'right' and check_point.check_connection('down-left'):
                    spot.directions[2][0] = -1



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

    def check_connection(self, direction: str) -> bool:
        """
        Функция, определяющая наличие связи вершины с другой вершиной
        по заданному направлению
        :param direction:
        :return: Есть ли связь
        """

        x, y = DIRECTION_ASSIGNMENT[direction]
        return bool(self.directions[x][y])

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


if __name__ == '__main__':
    Graph = GraphMap(3)

    for row in Graph.matrix:
        print(*row)

    for key, item in Graph.graph.items():
        print(key, item[0].directions, item[1])