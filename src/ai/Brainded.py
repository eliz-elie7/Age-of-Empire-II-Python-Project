from .General import General
from src.core import player
from src.core import map
from src.core import units
import math

"""Convention d'ordres pour tous les généraux
  {
    'type': str,           # Type d'action: 'attack', 'move', 'hold'
    'unit': Unit,          # Référence à l'unité qui exécute l'ordre
    'target': Unit,        # Unité cible (si type='attack')
    'position': (x, y)     # Position cible (si type='move')
}"""



class Brainded(General):
    def __init__(self):
        super().__init__("BrainDead")
        self.order_cooldown = 0.3  # 300ms entre les ordres
        self.last_order_time = 0

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        """Donne des ordres seulement aux unités qui en ont besoin"""
        orders = []
        
        for unit in units_needing_orders:
            enemies_in_sight = self.get_enemies_in_sight(unit, all_players)
            
            if enemies_in_sight:
                closest_enemy = self.get_closest_enemy(unit, enemies_in_sight)
                if unit.distance_to(closest_enemy) <= unit.get_range():
                    orders.append({'type': 'attack', 'unit': unit, 'target': closest_enemy})
        
        return orders

    def get_enemies_in_sight(self, unit, all_players):
        """Trouve les ennemis en ligne de vue"""
        enemies = []
        sight_range = unit.get_line_of_sight()
        
        for player in all_players:
            if player != unit.player:
                for enemy_unit in player.get_alive_units():
                    if unit.distance_to(enemy_unit) <= sight_range:
                        enemies.append(enemy_unit)
        return enemies

    def get_closest_enemy(self, unit, enemies):
        """Trouve l'ennemi le plus proche dans une liste"""
        if not enemies:
            return None
        
        closest_enemy = enemies[0]
        min_distance = unit.distance_to(closest_enemy)
        
        for enemy in enemies[1:]:
            distance = unit.distance_to(enemy)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        
        return closest_enemy