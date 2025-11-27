# general.py
from abc import ABC, abstractmethod

class General(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def give_orders(self, current_player, all_players, world_map, units_needing_orders):
        pass

    def get_name(self):
        return self.name

    # utilitaires partagés par les IA
    def enemies_in_sight(self, unit, all_players):
        enemies = []
        sight_range = unit.get_line_of_sight()
        for player in all_players:
            if player is unit.player:
                continue
            for enemy in player.get_alive_units():
                if not getattr(enemy, "is_alive", False):
                    continue
                if unit.distance_to(enemy) <= sight_range:
                    enemies.append(enemy)
        return enemies

    def all_enemies(self, unit, all_players):
        enemies = []
        for player in all_players:
            if player is unit.player:
                continue
            for enemy in player.get_alive_units():
                if getattr(enemy, "is_alive", False):
                    enemies.append(enemy)
        return enemies
