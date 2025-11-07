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


class Daft(General):
    def __init__(self):
        super().__init__("Daft")
        self.order_cooldown = 0.3

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        orders = []
        
        for unit in units_needing_orders:
            # Cherche d'abord les ennemis en vue
            enemies_in_sight = self.get_enemies_in_sight(unit, all_players)
            
            if enemies_in_sight:
                closest_enemy = self.get_closest_enemy(unit, enemies_in_sight)
                order = self._decide_combat_action(unit, closest_enemy, map)
            else:
                # Cherche l'ennemi le plus proche sur toute la carte
                all_enemies = self.get_all_enemies(unit, all_players)
                closest_enemy = self.get_closest_enemy(unit, all_enemies)
                order = self._decide_movement_action(unit, closest_enemy, map) if closest_enemy else {'type': 'hold', 'unit': unit}
            
            if order:
                orders.append(order)
        
        return orders

    def get_enemies_in_sight(self, unit, all_players):
        """Ennemis dans la ligne de vue"""
        enemies = []
        sight_range = unit.get_line_of_sight()
        
        for player in all_players:
            if player != unit.player:
                for enemy_unit in player.get_alive_units():
                    if unit.distance_to(enemy_unit) <= sight_range:
                        enemies.append(enemy_unit)
        return enemies

    def get_all_enemies(self, unit, all_players):
        """Tous les ennemis vivants"""
        enemies = []
        for player in all_players:
            if player != unit.player:
                enemies.extend(player.get_alive_units())
        return enemies

    def get_closest_enemy(self, unit, enemies):
        """Trouve l'ennemi le plus proche"""
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

    def _decide_combat_action(self, unit, enemy, map):
        """Décide attaque ou approche"""
        if unit.distance_to(enemy) <= unit.get_range():
            return {'type': 'attack', 'unit': unit, 'target': enemy}
        else:
            return self._calculate_movement_order(unit, enemy, map)

    def _decide_movement_action(self, unit, enemy, map):
        """Décide mouvement vers ennemi lointain"""
        return self._calculate_movement_order(unit, enemy, map) if enemy else {'type': 'hold', 'unit': unit}

    def _calculate_movement_order(self, unit, enemy, map):
        """Calcule une position d'approche intelligente"""
        dx = enemy.x - unit.x
        dy = enemy.y - unit.y
        distance = unit.distance_to(enemy)
        
        if distance == 0:
            return {'type': 'hold', 'unit': unit}
        
        # S'approcher avec marge pour éviter la collision
        approach_distance = distance - unit.get_range() + unit.get_collision_radius() + 10.0
        move_distance = min(unit.get_speed() * self.order_cooldown, approach_distance)
        
        target_x = unit.x + (dx / distance) * move_distance
        target_y = unit.y + (dy / distance) * move_distance
        
        # Vérifier que la position est valide
        if map.is_within_bounds(target_x, target_y):
            return {'type': 'move', 'unit': unit, 'position': (target_x, target_y)}
        else:
            return {'type': 'hold', 'unit': unit}