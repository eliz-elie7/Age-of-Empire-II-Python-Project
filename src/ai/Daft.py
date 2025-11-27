# ai_daft.py
from src.ai.General import General

class Daft(General):
    def __init__(self):
        super().__init__("Daft")

    def give_orders(self, current_player, all_players, world_map, units_needing_orders):
        orders = []
        for unit in units_needing_orders:
            enemies_in_sight = self.enemies_in_sight(unit, all_players)
            if enemies_in_sight:
                closest_enemy = self.get_closest_enemy(unit, enemies_in_sight)
                order = self._decide_combat_action(unit, closest_enemy, world_map)
            else:
                all_enemies = self.all_enemies(unit, all_players)
                closest_enemy = self.get_closest_enemy(unit, all_enemies)
                order = self._decide_movement_action(unit, closest_enemy, world_map) if closest_enemy else {'type': 'hold', 'unit': unit}
            if order:
                orders.append(order)
        return orders

    def get_closest_enemy(self, unit, enemies):
        if not enemies:
            return None
        closest = None
        min_d = None
        for e in enemies:
            if not getattr(e, "is_alive", False):
                continue
            d = unit.distance_to(e)
            if closest is None or d < min_d:
                closest = e
                min_d = d
        return closest

    def _decide_combat_action(self, unit, enemy, world_map):
        if enemy is None:
            return {'type': 'hold', 'unit': unit}
        if unit.distance_to(enemy) <= unit.get_range():
            return {'type': 'attack', 'unit': unit, 'target': enemy}
        else:
            return self._calculate_movement_order(unit, enemy, world_map)

    def _decide_movement_action(self, unit, enemy, world_map):
        return self._calculate_movement_order(unit, enemy, world_map) if enemy else {'type': 'hold', 'unit': unit}

    def _calculate_movement_order(self, unit, enemy, world_map):
        if enemy is None:
            return {'type': 'hold', 'unit': unit}
        dx = enemy.x - unit.x
        dy = enemy.y - unit.y
        distance = unit.distance_to(enemy)
        if distance == 0:
            return {'type': 'hold', 'unit': unit}
        approach_distance = max(0.0, distance - unit.get_range())
        move_distance = unit.get_speed() * 0.1  # correspond à ton prototype
        if distance > 0:
            move_factor = min(move_distance, approach_distance) / distance
        else:
            move_factor = 0.0
        target_x = unit.x + dx * move_factor
        target_y = unit.y + dy * move_factor
        return {'type': 'move', 'unit': unit, 'position': (target_x, target_y)}
