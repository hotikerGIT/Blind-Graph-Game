# Список строковых команд для направлений
DIRECTIONS = ['up-left', 'up', 'up-right',
              'left', 'mid', 'right',
              'down-left', 'down', 'down-right']

# Словарь предписания направлений, структуры "направление - индексы"
DIRECTION_ASSIGNMENT = {
    'up-left': (0, 0),
    'up': (0, 1),
    'up-right': (0, 2),
    'left': (1, 0),
    'right': (1, 2),
    'down-left': (2, 0),
    'down': (2, 1),
    'down-right': (2, 2)
}

# Словарь противоположных направлений
DIRECTION_OPPOSITES = {
    'up-left': 'down-right',
    'up': 'down',
    'up-right': 'down-left',
    'left': 'right',
    'right': 'left',
    'down-left': 'up-right',
    'down': 'up',
    'down-right': 'up-left'
}

# Список кортежей для получения индексов квадрата 3х3
MATRIX_ADJACENCY_DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 0), (0, 1),
    (1, -1), (1, 0), (1, 1)
]


# Функция для получения обратного направления
def get_reverse_direction(direction: str) -> str:
    return DIRECTION_OPPOSITES[direction]


# Список частот количества ребер, которые необходимо добавить к вершине
# после ее соединения с графом
EDGE_COUNT_CHANCES = [1, 1, 1,
                      2,
                      3, 3,
                      4,
                      5, 5,
                      6,
                      7]

LOOP_LIMIT = 50