# ai_braindead.py
from src.ai.General import General

class BrainDead(General):
    def __init__(self):
        super().__init__("BrainDead")

    def give_orders(self, current_player, all_players, world_map, units_needing_orders):
        orders = []
        for unit in units_needing_orders:
            enemies = self.enemies_in_sight(unit, all_players)
            if enemies:
                closest = self.get_closest_enemy(unit, enemies)
                if closest and unit.distance_to(closest) <= unit.get_range():
                    orders.append({'type': 'attack', 'unit': unit, 'target': closest})
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
