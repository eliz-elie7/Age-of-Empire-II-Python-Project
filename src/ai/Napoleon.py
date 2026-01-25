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

        # 2. CHOIX DE LA CIBLE PRIORITAIRE GLOBALE
        # On garde la logique : taper le plus faible pour réduire le nombre d'ennemis.
        primary_target = min(visible_enemies, key=lambda e: e.current_hp)

        # Seuil de distance (en pixels). 200 pixels = environ 6 cases (6 * 32).
        # Si un soldat est plus loin que ça, il ne doit pas essayer de rejoindre la mêlée centrale.
        MAX_FOCUS_DISTANCE = 200.0

        for unit in units_needing_orders:
            dist_to_primary = unit.distance_to(primary_target)

            # --- LOGIQUE INTELLIGENTE ANTI-BOUCHON ---
            
            # Cas A : Je suis assez près de la cible prioritaire -> JE FOCUS
            if dist_to_primary <= MAX_FOCUS_DISTANCE:
                orders.append({'type': 'attack', 'unit': unit, 'target': primary_target})
            
            # Cas B : Je suis trop loin -> J'attaque le plus proche pour avancer
            else:
                closest_local = self.get_closest(unit, visible_enemies)
                if closest_local:
                    orders.append({'type': 'attack', 'unit': unit, 'target': closest_local})
        
        return orders

    def get_visible_enemies(self, current_player, all_players):
        enemies = []
        for p in all_players:
            if p != current_player:
                enemies.extend(p.get_alive_units())
        return enemies

    def get_closest(self, unit, candidates):
        if not candidates: return None
        return min(candidates, key=lambda e: unit.distance_to(e))