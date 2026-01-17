import math
from typing import List

class Map:
    """Classe Map - Gestion du terrain et collisions"""

    def __init__(self, width: float, height: float, collision_allowance: float = 0.5):
        self.width = width
        self.height = height

        # collision_allowance ∈ (0, 1]
        # plus petit => plus permissif
        self.collision_allowance = max(0.6, min(1.0, collision_allowance))

    # --------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------

    def is_within_bounds(self, x: float, y: float) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_width(self) -> float:
        return self.width

    def get_height(self) -> float:
        return self.height

    # --------------------------------------------------
    # CLAMP POSITION (ANTI SORTIE DE MAP)
    # --------------------------------------------------

    def clamp_position(self, x: float, y: float):
        clamped_x = max(0.0, min(self.width - 1e-3, x))
        clamped_y = max(0.0, min(self.height - 1e-3, y))
        return clamped_x, clamped_y

    # --------------------------------------------------
    # COLLISIONS & MOUVEMENT
    # --------------------------------------------------

    def can_move_to(self, unit, target_x: float, target_y: float, all_units: List) -> bool:
        # limites carte
        if not self.is_within_bounds(target_x, target_y):
            return False

        for other in all_units:
            if other is unit:
                continue
            if not getattr(other, 'is_alive', True):
                continue

            # unités partageant l’espace
            try:
                if other.can_occupy_same_space(unit) or unit.can_occupy_same_space(other):
                    continue
            except Exception:
                pass

            dx = other.x - target_x
            dy = other.y - target_y
            dist_sq = dx * dx + dy * dy

            sum_r = other.get_collision_radius() + unit.get_collision_radius()

            # distance minimale réaliste
            min_dist = sum_r * self.collision_allowance

            if dist_sq < min_dist * min_dist:
                return False

        return True

    # --------------------------------------------------
    # RECHERCHE D’UNITÉS
    # --------------------------------------------------

    def get_units_at_position(
        self,
        x: float,
        y: float,
        radius: float,
        all_units: List
    ) -> List:
        units_in_range = []

        for unit in all_units:
            if unit.is_alive:
                dx = unit.x - x
                dy = unit.y - y
                if dx * dx + dy * dy <= radius * radius:
                    units_in_range.append(unit)

        return units_in_range

    def get_units_in_line_of_sight(self, unit, all_units: List) -> List:
        units_in_sight = []
        sight_range = unit.get_line_of_sight()

        for other in all_units:
            if other is unit or not other.is_alive:
                continue

            if unit.distance_to(other) <= sight_range:
                units_in_sight.append(other)

        return units_in_sight

    # --------------------------------------------------
    # SPAWN INTELLIGENT
    # --------------------------------------------------

    def find_spawn_position(
        self,
        unit,
        desired_x: float,
        desired_y: float,
        all_units: List,
        max_radius: float = 200.0,
        step: float = 8.0
    ):
        desired_x, desired_y = self.clamp_position(desired_x, desired_y)

        if self.can_move_to(unit, desired_x, desired_y, all_units):
            return desired_x, desired_y

        r = step
        two_pi = 2 * math.pi

        while r <= max_radius:
            samples = max(8, int((two_pi * r) / step))
            for i in range(samples):
                angle = (two_pi * i) / samples
                nx = desired_x + math.cos(angle) * r
                ny = desired_y + math.sin(angle) * r
                nx, ny = self.clamp_position(nx, ny)

                if self.can_move_to(unit, nx, ny, all_units):
                    return nx, ny

            r += step

        return desired_x, desired_y