# TODO: исправить функцию create_connections


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

        self.fill_matrix()
        self.connect_graph()

    def add_spot_to_matrix(self, new_spot: 'Spot') -> None:
        """
        Функция добавления вершины в случайное место в матрице, причем
        вершина должна находиться вблизи с остальными
        :param new_spot: новая вершина
        :return:
        """

        # Итерируемся, пока не найдем место для вершины
        # причем размеры матрицы рассчитаны так, что место всегда найдется
        while True:
            # Создаем список занятых координат
            taken_cords = [(x, y) for _, (x, y) in self.graph.values()]

            # Выбираем случайные координаты
            x, y = random.choice(taken_cords)

            # Создаем список для направлений и случайно перемешиваем его
            directions = MATRIX_ADJACENCY_DIRECTIONS[:]
            random.shuffle(directions)

            toggle = False
            for delta_x, delta_y in directions:
                new_x = x + delta_x
                new_y = y + delta_y

                # Если новые координаты указывают на уже существующую вершину, пропускаем итерацию
                if (new_x, new_y) in taken_cords:
                    continue

                # Занимаем свободное место и добавляем его в граф
                self.matrix[new_x][new_y] = new_spot.spot_name
                self.graph[new_spot.spot_name] = (new_spot, (new_x, new_y))

                toggle = True
                break

            if toggle:
                break

    def fill_matrix(self) -> None:
        for spot_name in range(2, self.spots_amount + 1):
            self.add_spot_to_matrix(Spot(spot_name))

    def get_scope(self, spot_name: int) -> list[int]:
        """
        Функция, возвращающая все вершины в квадрате 3х3, центром которого
        является вершина по заданному имени
        :param spot_name: имя нужной вершины
        :return:
        """
        res = []

        _, (cur_x, cur_y) = self.graph[spot_name]

        for x, y in MATRIX_ADJACENCY_DIRECTIONS:
            res.append(self.matrix[cur_x + x][cur_y + y])

        return res

    def create_connections(self, spot: 'Spot') -> None:
        spot_name = spot.spot_name

        scope: list[int] = self.get_scope(spot_name)
        possible_connections = {name: DIRECTIONS[index]
                                for index, name in enumerate(scope)
                                if name and name != spot_name}

        already_connected = sum(1 for row in spot.directions for i in row if i != spot_name and i)
        to_connect = random.choice(EDGE_COUNT_CHANCES)

        if already_connected < to_connect:
            potential_connections: list[int] = list(possible_connections.keys())
            needed_connections = to_connect - already_connected

            done_connections = 0
            loop_warning = 0
            while done_connections != needed_connections:
                loop_warning += 1

                if loop_warning == 1_000:
                    raise ValueError('Невозможно создать нужное количество ребер')

                new_point_name: int = random.choice(potential_connections)
                new_point: 'Spot' = self.graph[new_point_name][0]
                current_direction = possible_connections[new_point_name]
                direction_to_check = DIRECTION_OPPOSITES[current_direction]

                if not new_point.check_connection(direction_to_check):
                    other_x, other_y = DIRECTION_ASSIGNMENT[direction_to_check]
                    cur_x, cur_y = DIRECTION_ASSIGNMENT[current_direction]

                    new_point.directions[other_x][other_y] = spot_name
                    spot.directions[cur_x][cur_y] = new_point_name

                    done_connections += 1

    def connect_graph(self):
        for spot, _ in self.graph.values():
            self.create_connections(spot)

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
    Graph = GraphMap(10)

    for row in Graph.matrix:
        print(*row)

    for key, item in Graph.graph.items():
        print(key, item[0].directions, item[1])