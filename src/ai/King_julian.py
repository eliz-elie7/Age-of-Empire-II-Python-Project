from .General import General

class King_julian(General):
    def __init__(self):
        super().__init__("Daft_Tactical")
        self.strategy = "UNDECIDED"

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        orders = []
        
        # 1. ANALYSE : Identification des forces en présence
        my_alive_units = current_player.get_alive_units()
        if not my_alive_units:
            return []

        # Extraction des types (on suppose que unit.unit_type existe)
        archers = [u for u in my_alive_units if u.unit_type == "ARCHER"]
        cavalry = [u for u in my_alive_units if u.unit_type == "CAVALRY"]
        infantry = [u for u in my_alive_units if u.unit_type == "INFANTRY"]

        # OMNISCIENCE : On récupère tous les ennemis vivants via la classe Player
        all_enemies = []
        for player in all_players:
            if player != current_player:
                all_enemies.extend(player.get_alive_units())
        
        if not all_enemies:
            return [{'type': 'hold', 'unit': u} for u in units_needing_orders]

        # 2. DÉCISION DU CRITÈRE (Le plus pertinent : La mobilité vs Distance)
        # Si on a de la cavalerie (>20% de l'armée), on tente le Marteau et l'Enclume
        if len(cavalry) > len(my_alive_units) * 0.2:
            self.strategy = "HAMMER_AND_ANVIL"
        # Sinon, si on a beaucoup d'archers, on joue la distance
        elif len(archers) > len(my_alive_units) * 0.4:
            self.strategy = "HARASSMENT"
        else:
            self.strategy = "DIRECT_ASSAULT"

        # 3. ATTRIBUTION DES ORDRES
        for unit in units_needing_orders:
            closest_enemy = self.get_closest_enemy(unit, all_enemies)
            
            if self.strategy == "HARASSMENT" and unit.unit_type == "ARCHER":
                orders.append(self._order_harass(unit, closest_enemy))
            
            elif self.strategy == "HAMMER_AND_ANVIL":
                if unit.unit_type == "CAVALRY":
                    # Le Marteau : cherche l'ennemi le plus faible ou le plus loin
                    target = self._get_flank_target(all_enemies)
                    orders.append({'type': 'attack', 'unit': unit, 'target': target})
                else:
                    # L'Enclume : fixe l'ennemi le plus proche
                    orders.append({'type': 'attack', 'unit': unit, 'target': closest_enemy})
            
            else:
                # Comportement par défaut (ton code original)
                orders.append({'type': 'attack', 'unit': unit, 'target': closest_enemy})

        return orders

    def _order_harass(self, unit, enemy):
        """Logique de micro-gestion des archers (Hit & Run)"""
        dist = unit.distance_to(enemy)
        # Si l'ennemi est trop proche (danger), on bat en retraite
        if dist < unit.get_range() * 0.6:
            # Calcul d'un vecteur de fuite simple
            flee_x = unit.x - (enemy.x - unit.x)
            flee_y = unit.y - (enemy.y - unit.y)
            return {'type': 'move', 'unit': unit, 'position': (flee_x, flee_y)}
        # Sinon on attaque
        return {'type': 'attack', 'unit': unit, 'target': enemy}

    def _get_flank_target(self, enemies):
        """Cible les unités fragiles (Archers) ou entamées"""
        archers = [e for e in enemies if e.unit_type == "ARCHER"]
        if archers:
            return archers[0]
        # Sinon cible avec le moins de points de vie (getattr pour sécurité)
        return min(enemies, key=lambda e: getattr(e, 'hp', 100))

    def get_closest_enemy(self, unit, enemies):
        if not enemies: return None
        return min(enemies, key=lambda e: unit.distance_to(e))
