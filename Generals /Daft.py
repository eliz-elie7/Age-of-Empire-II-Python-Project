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

class Daft(General):

    def give_orders(self, current_player, all_players, map):
        myunits = current_player.get_alive_units()
        return self._process_all_units(myunits, all_players, current_player) 

    def get_enemy(self, all_players, current_player):
        enemy_player = all_players[0] if current_player == all_players[1] else all_players[1]
        return enemy_player.get_alive_units()

    def get_enemies_in_sight(self, unit, all_players): 
        enemies = []
        sight_range = unit.get_line_of_sight()
        for player in all_players:
            if player != unit.player:
                for enemy_unit in player.get_alive_units():
                    if unit.distance_to(enemy_unit) <= sight_range:
                        enemies.append(enemy_unit)
        return enemies

    def closest_enemy(self, unit, all_enemies):
        if not all_enemies: return None
        distance = unit.distance_to(all_enemies[0])
        closest_enemy = all_enemies[0]
        for enemy in all_enemies:
            dis = unit.distance_to(enemy)
            if distance >= dis:
                distance = dis
                closest_enemy = enemy
        return closest_enemy

    def _decide_unit_action(self, unit, enemies_in_sight, all_players, current_player):
        if enemies_in_sight:
            first_enemy = enemies_in_sight[0]
            if unit.distance_to(first_enemy) <= unit.get_range():  
                return {'type': 'attack', 'unit': unit, 'target': first_enemy}
            else:
                return {'type': 'move', 'unit': unit, 'position': (first_enemy.x, first_enemy.y)}  
        else:
            enemy_units = self.get_enemy(all_players, current_player)
            closest_enemy = self.closest_enemy(unit, enemy_units)
            if not closest_enemy:
                return {'type': 'hold', 'unit': unit}
            else:
                return {'type': 'move', 'unit': unit, 'position': (closest_enemy.x, closest_enemy.y)}

    def _process_all_units(self, myunits, all_players, current_player):
        orders = []
        for unit in myunits:
            enemies_in_sight = self.get_enemies_in_sight(unit, all_players)
            order = self._decide_unit_action(unit, enemies_in_sight, all_players, current_player)
            orders.append(order)
        return orders