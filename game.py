import random
from map_generating import GraphMap
from values import DIFFICULTY_ASSIGNMENT
from player import Player


class Game:
    def __init__(self, difficulty):
        self.parameters = DIFFICULTY_ASSIGNMENT[difficulty]

        self.spots_amount = random.randint(self.parameters['size-low'], self.parameters['size-high'])
        self.map = GraphMap(self.spots_amount)

        self.player_tile: int = 1
        self.enemy_tile: int = random.choice(list(self.map.graph.keys()))

        if self.enemy_tile == 1:
            self.enemy_tile = self.spots_amount

        self.player = Player(self.map.graph[self.player_tile][0])
        self.enemy = Player(self.map.graph[self.enemy_tile][0])