import math
from typing import List

class Map:
    """Classe Map - Gestion du terrain et collisions"""
    
    def __init__(self, width: float, height: float, collision_allowance: float = 0.4):
        self.width = width
        self.height = height
        # collision_allowance ∈ (0, 1] réduit la distance minimale requise entre unités
        # 1.0 = pas de changement (séparation stricte), plus petit => plus permissif (autorise chevauchement)
        self.collision_allowance = max(0.05, min(1.0, collision_allowance))
    
    def is_within_bounds(self, x: float, y: float) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_width(self) -> float:
        return self.width
    
    def get_height(self) -> float:
        return self.height
    
    def can_move_to(self, unit, target_x: float, target_y: float, all_units: List) -> bool:
        # Vérifie les limites
        if not self.is_within_bounds(target_x, target_y):
            return False

        # Vérifie collisions simples avec les autres unités (empêche chevauchement strict)
        for other in all_units:
            if other is unit:
                continue
            if not getattr(other, 'is_alive', True):
                continue

            # Si une des deux unités peut partager l'espace, on ignore la collision
            try:
                can_share = other.can_occupy_same_space(unit) or unit.can_occupy_same_space(other)
            except Exception:
                can_share = False

            if can_share:
                continue

            dx = other.x - target_x
            dy = other.y - target_y
            dist_sq = dx*dx + dy*dy

            # Calcul de la distance minimale autorisée en tenant compte de la tolérance
            base_min_dist = (other.get_collision_radius() + unit.get_collision_radius()) * self.collision_allowance

            # epsilon relatif (10% de la somme des radii) pour éviter blocages suite à l'échelle
            min_dist = max(base_min_dist, 0.1 * (other.get_collision_radius() + unit.get_collision_radius()), 0.5)

            # Autoriser le rapprochement jusqu'à la portée d'attaque (utile quand range est petit)
            try:
                attack_threshold = max(unit.get_range() + other.get_collision_radius(), 0.5)
                if dist_sq <= (attack_threshold * attack_threshold):
                    continue
            except Exception:
                pass

            if dist_sq < (min_dist * min_dist):
                return False

        return True
    
    def get_units_at_position(self, x: float, y: float, radius: float, all_units: List) -> List:
        units_in_range = []
        for unit in all_units:
            if unit.is_alive:
                distance = math.sqrt((unit.x - x)**2 + (unit.y - y)**2)
                if distance <= radius:
                    units_in_range.append(unit)
        return units_in_range
    
    def get_units_in_line_of_sight(self, unit, all_units: List) -> List:
        units_in_sight = []
        sight_range = unit.get_line_of_sight()
        
        for other_unit in all_units:
            if other_unit != unit and other_unit.is_alive:
                if unit.distance_to(other_unit) <= sight_range:
                    units_in_sight.append(other_unit)
        
        return units_in_sight
    
    def clamp_position(self, x: float, y: float) -> (float, float):
        """Ramène une position à l'intérieur des bords de la carte."""
        clamped_x = max(0.0, min(self.width - 1e-3, x))
        clamped_y = max(0.0, min(self.height - 1e-3, y))
        return clamped_x, clamped_y

    def find_spawn_position(self, unit, desired_x: float, desired_y: float, all_units: List,
                            max_radius: float = 200.0, step: float = 8.0) -> (float, float):
        """
        Cherche une position proche de (desired_x, desired_y) où `unit` peut se placer
        sans collision selon can_move_to. Recherche en anneaux.
        """
        # Clamp initial
        desired_x, desired_y = self.clamp_position(desired_x, desired_y)

        # Si la position souhaitée est déjà valide -> retourne
        if self.can_move_to(unit, desired_x, desired_y, all_units):
            return desired_x, desired_y

        # Recherche en anneaux (spirale)
        r = step
        two_pi = 2 * math.pi
        while r <= max_radius:
            # Déterminer un nombre d'échantillons proportionnel au périmètre
            samples = max(8, int((two_pi * r) / step))
            for i in range(samples):
                angle = (two_pi * i) / samples
                nx = desired_x + math.cos(angle) * r
                ny = desired_y + math.sin(angle) * r
                nx, ny = self.clamp_position(nx, ny)
                if self.can_move_to(unit, nx, ny, all_units):
                    return nx, ny
            r += step

        # Si rien trouvé, renvoyer la position clampée (fallback)
        return desired_x, desired_y
