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
        """Заполнение матрицы путем итеративного добавления точек"""
        for spot_name in range(2, self.spots_amount + 1):
            self.add_spot_to_matrix(Spot(spot_name))

    def get_scope(self, spot_name: int) -> list[int]:
        """
        Функция, возвращающая все вершины в квадрате 3х3, центром которого
        является вершина по заданному имени, в виде одномерного списка
        :param spot_name: имя нужной вершины
        :return:
        """

        res = []

        _, (cur_x, cur_y) = self.graph[spot_name]

        for x, y in MATRIX_ADJACENCY_DIRECTIONS:
            res.append(self.matrix[cur_x + x][cur_y + y])

        return res

    def create_connections(self, spot: 'Spot') -> None:
        """
        Создание ребер графа путем выбора точки и соединяя ее с уже созданными.
        Меняет не граф, а значения directions для точек
        :param spot: точка, которую нужно соединить
        :return:
        """

        spot_name = spot.spot_name

        # Получаем квадрат 3х3, содержащий возможные соединения для точки
        scope: list[int] = self.get_scope(spot_name)

        # Словарь возможных соединений типа имя точки: направление
        possible_connections: dict[int, str] = {name: DIRECTIONS[index]
                                for index, name in enumerate(scope)
                                if name and name != spot_name and name != -1}

        # Переменная, хранящая количество существующих соединений для заданной точки
        already_connected = sum(1 for row in spot.directions
                                for i in row
                                if i != spot and i is not None and not isinstance(i, NullSpot))

        # Регуляция количества ребер
        pick = [i for i in EDGE_COUNT_CHANCES if i <= len(possible_connections)]

        # В случае, если невозможно создать новых ребер, выходим из функции
        if not pick:
            return

        to_connect = random.choice(pick)

        if already_connected < to_connect:
            # Список имен точек
            potential_connections: list[int] = list(possible_connections.keys())
            needed_connections = to_connect - already_connected

            done_connections = 0  # Счетчик созданных ребер
            loop_warning = 0
            while done_connections != needed_connections:
                loop_warning += 1

                if loop_warning == LOOP_LIMIT:
                    break

                # Выбор точки, которую будем пытаться соединить
                new_point_name: int = random.choice(potential_connections)
                new_point: 'Spot' = self.graph[new_point_name][0]

                # Получаем взаимообратные направления
                current_direction: str = possible_connections[new_point_name]
                direction_to_check: str = DIRECTION_OPPOSITES[current_direction]

                # Проверяем отсутствие соединения у выбранной точки по данному направлению
                if not new_point.check_connection(direction_to_check):
                    other_x, other_y = DIRECTION_ASSIGNMENT[direction_to_check]
                    cur_x, cur_y = DIRECTION_ASSIGNMENT[current_direction]

                    # Обновляем хранилища направлений выбранных точек
                    new_point.directions[other_x][other_y] = spot
                    spot.directions[cur_x][cur_y] = new_point

                    # Убираем возможность пересечений ребер для каждой точки
                    self.disallow_intersections(new_point)
                    self.disallow_intersections(spot)

                    done_connections += 1

    def connect_graph(self):
        """Создание ребер графа путем добавления в него новых точек и соединения """
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

        scope = self.get_scope(spot.spot_name)
        directions_shortcut = spot.directions

        if scope[1]:
            check = self.graph[spot.spot_name][0]

            if check.check_connection('down-left'):
                directions_shortcut[0][0] = NullSpot()

            if check.check_connection('down-right'):
                directions_shortcut[0][2] = NullSpot()

        if scope[7]:
            check = self.graph[spot.spot_name][0]

            if check.check_connection('up-left'):
                directions_shortcut[2][0] = NullSpot()

            if check.check_connection('up-right'):
                directions_shortcut[2][2] = NullSpot()


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
        self.directions = ([None, None, None],
                           [None, self, None],
                           [None, None, None])

        self.is_special = False

    def check_connection(self, direction: str) -> bool:
        """
        Функция, определяющая наличие связи вершины с другой вершиной
        по заданному направлению
        :param direction:
        :return: Есть ли связь
        """

        x, y = DIRECTION_ASSIGNMENT[direction]
        return bool(self.directions[x][y])


class NullSpot(Spot):
    """
    Класс, показывающий невозможность создания ребра по заданному направлению
    """
    def __init__(self):
        super().__init__(-1)


def testing():
    random_size = random.randint(1, 100)
    graph = GraphMap(random_size)


if __name__ == '__main__':
    graph = GraphMap(10)

    for test_row in graph.matrix:
        print(*test_row)