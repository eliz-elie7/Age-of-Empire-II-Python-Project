from .General import General
#from core.player import Player
from Units import unit
#from core.map import Map 

"""Convention d'ordres pour tous les généraux
  {
    'type': str,           # Type d'action: 'attack', 'move', 'hold'
    'unit': Unit,          # Référence à l'unité qui exécute l'ordre
    'target': Unit,        # Unité cible (si type='attack')
    'position': (x, y)     # Position cible (si type='move')
}"""

class Brainded(General):

    def give_orders(self, current_player, all_players, map):
        myunits = current_player.get_alive_units()
        return self._process_all_units(myunits, all_players)

    def get_enemies_in_sight(self, unit, all_players):
        """Seule méthode nécessaire pour BrainDead"""
        enemies = []
        sight_range = unit.get_line_of_sight()
        for player in all_players:
            if player != unit.player:
                for enemy_unit in player.get_alive_units():
                    if unit.distance_to(enemy_unit) <= sight_range:
                        enemies.append(enemy_unit)
        return enemies

    def _decide_unit_action(self, unit, enemies_in_sight):
        if enemies_in_sight:
            first_enemy = enemies_in_sight[0]
            if unit.distance_to(first_enemy) <= unit.get_range():
                return {'type': 'attack', 'unit': unit, 'target': first_enemy}
        return {'type': 'hold', 'unit': unit}

    def _process_all_units(self, myunits, all_players):
        orders = []
        for unit in myunits:
            enemies_in_sight = self.get_enemies_in_sight(unit, all_players)
            order = self._decide_unit_action(unit, enemies_in_sight)
            orders.append(order)
        return orders