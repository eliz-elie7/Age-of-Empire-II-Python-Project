import math
import random
from typing import List, Tuple

# On s'assure que TILE est défini (32.0 par défaut dans ton projet)
TILE = 32.0

class Map:
    """Classe Map - Gestion du terrain, collisions, recherche d'unités et élévation"""

    def __init__(self, width: float, height: float, collision_allowance: float = 0.5):
        self.width = width
        self.height = height

        # 1. Gestion des collisions (ton code)
        # collision_allowance ∈ (0, 1]
        self.collision_allowance = max(0.6, min(1.0, collision_allowance))

        # 2. Initialisation de l'élévation (Ajout)
        self.grid_w = int(width // TILE)
        self.grid_h = int(height // TILE)
        
        # Génération 50% niv 0, 30% niv 1, 20% niv 2
        self.elevation_grid = []
        for i in range(self.grid_w):
            column = []
            for j in range(self.grid_h):
                r = random.random()
                level = 0 if r < 0.50 else (1 if r < 0.80 else 2)
                column.append(level)
            self.elevation_grid.append(column)
        
        # Lissage pour créer des zones cohérentes
        self._smooth_elevation()

    def _smooth_elevation(self):
        """Lissage pour éviter l'effet damier et créer des collines groupées"""
        for _ in range(2):
            new_grid = [row[:] for row in self.elevation_grid]
            for i in range(1, self.grid_w - 1):
                for j in range(1, self.grid_h - 1):
                    neighbors = [
                        self.elevation_grid[i-1][j], self.elevation_grid[i+1][j],
                        self.elevation_grid[i][j-1], self.elevation_grid[i][j+1]
                    ]
                    new_grid[i][j] = round(sum(neighbors) / len(neighbors))
            self.elevation_grid = new_grid

    # --------------------------------------------------
    # NOUVELLE FONCTION ÉLÉVATION
    # --------------------------------------------------

    def get_elevation_at(self, x: float, y: float) -> int:
        ix, iy = int(x // TILE), int(y // TILE)
        if 0 <= ix < self.grid_w and 0 <= iy < self.grid_h:
            return self.elevation_grid[ix][iy]
        return 0

    # --------------------------------------------------
    # DIMENSIONS (Ton code conservé)
    # --------------------------------------------------

    def is_within_bounds(self, x: float, y: float) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_width(self) -> float:
        return self.width

    def get_height(self) -> float:
        return self.height

    def clamp_position(self, x: float, y: float):
        clamped_x = max(0.0, min(self.width - 1e-3, x))
        clamped_y = max(0.0, min(self.height - 1e-3, y))
        return clamped_x, clamped_y

    # --------------------------------------------------
    # COLLISIONS & MOUVEMENT (Mis à jour avec élévation)
    # --------------------------------------------------

    def can_move_to(self, unit, target_x: float, target_y: float, all_units: List) -> bool:
        # limites carte
        if not self.is_within_bounds(target_x, target_y):
            return False

        # --- Logique de pente (Ajout) ---
        curr_el = self.get_elevation_at(unit.x, unit.y)
        next_el = self.get_elevation_at(target_x, target_y)
        if abs(next_el - curr_el) > 1: # Bloque si saut de niveau direct (falaise)
            return False

        # --- Collisions unités (Ton choix de laisser glisser) ---
        # On laisse la séparation douce gérer les contacts entre unités
        return True

    # --------------------------------------------------
    # RECHERCHE D’UNITÉS (Ton code intégralement conservé)
    # --------------------------------------------------

    def get_units_at_position(self, x: float, y: float, radius: float, all_units: List) -> List:
        units_in_range = []
        for unit in all_units:
            if getattr(unit, 'is_alive', True):
                dx, dy = unit.x - x, unit.y - y
                if dx * dx + dy * dy <= radius * radius:
                    units_in_range.append(unit)
        return units_in_range

    def get_units_in_line_of_sight(self, unit, all_units: List) -> List:
        units_in_sight = []
        sight_range = unit.get_line_of_sight()
        for other in all_units:
            if other is unit or not getattr(other, 'is_alive', True):
                continue
            if unit.distance_to(other) <= sight_range:
                units_in_sight.append(other)
        return units_in_sight

    # --------------------------------------------------
    # SPAWN INTELLIGENT (Ton code intégralement conservé)
    # --------------------------------------------------

    def find_spawn_position(self, unit, desired_x: float, desired_y: float, all_units: List, max_radius: float = 200.0, step: float = 8.0):
        desired_x, desired_y = self.clamp_position(desired_x, desired_y)

        if self.can_move_to(unit, desired_x, desired_y, all_units):
            return desired_x, desired_y

        r = step
        two_pi = 2 * math.pi
        while r <= max_radius:
            samples = max(8, int((two_pi * r) / step))
            for i in range(samples):
                angle = (two_pi * i) / samples
                nx, ny = self.clamp_position(desired_x + math.cos(angle) * r, desired_y + math.sin(angle) * r)
                if self.can_move_to(unit, nx, ny, all_units):
                    return nx, ny
            r += step
        return desired_x, desired_y