import random
from .General import General
from ..core.units import Crossbowman, Knight, Pikeman, LongSwordsman, EliteSkirmisher

class SunTzu(General):
    """
    Général Stratège :
    1. Utilise les contres (Piquiers vs Chevaliers, etc.)
    2. Kiting (Hit & Run) pour les archers.
    3. Focus sur les unités faibles ou dangereuses.
    """
    def __init__(self):
        super().__init__("SunTzu")

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        orders = []
        
        # Récupération de tous les ennemis visibles une seule fois pour optimiser
        visible_enemies = self.get_all_visible_enemies(current_player, all_players)
        
        if not visible_enemies:
            # Si personne n'est visible, on peut soit attendre, soit explorer
            # Pour l'instant, on reste en position (Hold) ou on patrouille
            return []

        for unit in units_needing_orders:
            order = self.decide_unit_action(unit, visible_enemies, map)
            if order:
                orders.append(order)
        
        return orders

    def decide_unit_action(self, unit, enemies, map):
        # 1. Identifier les cibles prioritaires selon le type de mon unité
        targets = self.filter_targets_by_counter(unit, enemies)
        
        if not targets:
            # Fallback : Si pas de contre idéal, attaquer l'ennemi le plus proche
            targets = enemies
            
        # Trouver la cible la plus proche parmi les candidates
        best_target = self.get_closest_unit(unit, targets)
        
        if not best_target:
            return None

        dist = unit.distance_to(best_target)

        # 2. Comportement Spécial : Archers (Crossbowman) -> Hit & Run
        if isinstance(unit, Crossbowman):
            safe_distance = unit.get_range() * 0.7  # Marge de sécurité
            
            # Si l'ennemi est trop près et qu'on peut reculer
            if dist < safe_distance:
                # Calcul d'une position de fuite (vecteur opposé à l'ennemi)
                retreat_pos = self.calculate_retreat_position(unit, best_target, map)
                return {'type': 'move', 'unit': unit, 'position': retreat_pos}
            
            # Sinon, si on est à portée, on tire
            elif dist <= unit.get_range():
                 return {'type': 'attack', 'unit': unit, 'target': best_target}
            
            # Sinon on s'approche (mais pas trop près)
            else:
                 return {'type': 'attack', 'unit': unit, 'target': best_target}

        # 3. Comportement Standard (Mêlée)
        return {'type': 'attack', 'unit': unit, 'target': best_target}

    def filter_targets_by_counter(self, unit, enemies):
        """Retourne une sous-liste d'ennemis que mon unité contre naturellement."""
        if isinstance(unit, Pikeman):
            # Les piquiers chassent les chevaliers
            return [e for e in enemies if isinstance(e, Knight)]
        
        elif isinstance(unit, Knight):
            # Les chevaliers chassent les archers (et autres unités fragiles)
            return [e for e in enemies if isinstance(e, Crossbowman)]
        
        elif isinstance(unit, Crossbowman):
            # Les arbalétriers chassent l'infanterie lente (Piquiers)
            return [e for e in enemies if isinstance(e, Pikeman)]
        
        return enemies # Pas de préférence spécifique

    def get_all_visible_enemies(self, current_player, all_players):
        """Récupère tous les ennemis vivants des autres joueurs."""
        enemies = []
        for p in all_players:
            if p != current_player:
                enemies.extend(p.get_alive_units())
        return enemies

    def get_closest_unit(self, unit, candidates):
        if not candidates:
            return None
        return min(candidates, key=lambda e: unit.distance_to(e))

    def calculate_retreat_position(self, unit, enemy, map):
        """Calcule une position pour s'éloigner de l'ennemi."""
        # Vecteur Ennemi -> Unité
        dx = unit.x - enemy.x
        dy = unit.y - enemy.y
        
        # Normalisation (si distance nulle, fuite aléatoire)
        dist = (dx**2 + dy**2)**0.5
        if dist == 0:
            dx, dy = 1, 0
        else:
            dx, dy = dx/dist, dy/dist
            
        # Fuir de "k" distance
        flee_distance = 50.0 
        target_x = unit.x + dx * flee_distance
        target_y = unit.y + dy * flee_distance
        
        # S'assurer qu'on ne sort pas de la carte (Clamp)
        return map.clamp_position(target_x, target_y)