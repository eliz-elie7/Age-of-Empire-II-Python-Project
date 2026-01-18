from .General import General

class Napoleon(General):
    def __init__(self):
        super().__init__("Napoleon")

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        orders = []
        
        # 1. Identifier tous les ennemis
        visible_enemies = self.get_visible_enemies(current_player, all_players)
        
        if not visible_enemies:
            return []

        # 2. CHOIX DE LA CIBLE PRIORITAIRE (FOCUS FIRE)
        # On choisit l'ennemi le plus "facile" à tuer pour réduire le nombre d'adversaires rapidement.
        # Critère : Celui qui a le moins de PV actuels, ou le plus proche.
        primary_target = min(visible_enemies, key=lambda e: (e.current_hp, self.get_avg_distance(e, units_needing_orders)))

        # 3. Tout le monde attaque la MEME cible (si à portée/faisable)
        for unit in units_needing_orders:
            # Si l'unité est trop loin de la cible prioritaire, elle peut taper le plus proche en attendant
            # Mais l'idéal est de converger vers la cible prioritaire.
            orders.append({'type': 'attack', 'unit': unit, 'target': primary_target})
        
        return orders

    def get_visible_enemies(self, current_player, all_players):
        enemies = []
        for p in all_players:
            if p != current_player:
                enemies.extend(p.get_alive_units())
        return enemies

    def get_avg_distance(self, enemy, my_units):
        """Calcule la distance moyenne entre un ennemi et mon armée (pour éviter de focus un mec à l'autre bout de la map)"""
        if not my_units: return 0
        total_dist = sum(unit.distance_to(enemy) for unit in my_units)
        return total_dist / len(my_units)