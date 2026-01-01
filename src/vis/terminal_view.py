# terminal_view.py --- IGNORE ---

import os
import math
import time
from typing import Dict, Any


class TerminalView:
    """Vue terminal ASCII pour MedievAIl."""

    def __init__(self, fps: int = 25):
        self.fps = fps
        self._running = True

        # Taille logique : 1 case ≈ TILE pixels
        self.grid_size_factor = 32.0

        self.min_width = 60
        self.min_height = 20

    def is_running(self) -> bool:
        return self._running

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw(self, state: Dict[str, Any], world_map):
        if not self._running:
            return

        self._clear_screen()

        # ============================
        #   Infos globales
        # ============================
        meta = state["meta"]

        width_map = world_map.get_width()
        height_map = world_map.get_height()

        grid_width = max(self.min_width, math.ceil(width_map / self.grid_size_factor))
        grid_height = max(self.min_height, math.ceil(height_map / self.grid_size_factor))

        # Grille vide
        grid = [['.' for _ in range(grid_width)] for _ in range(grid_height)]

        # ============================
        #   Placement des unités
        # ============================
        for unit in state["units"]:
            gx = int(unit["position"][0] / self.grid_size_factor)
            gy = int(unit["position"][1] / self.grid_size_factor)

            if 0 <= gx < grid_width and 0 <= gy < grid_height:
                # Une seule lettre par unité (lisible)
                symbol = unit["owner"][0].upper()
                grid[gy][gx] = symbol

        output = []

        # ============================
        #   Résumé joueurs
        # ============================
        output.append("JOUEURS")
        for p in state["players"]:
            output.append(
                f"  {p['name']}: {p['alive_units']} / {p['total_units']} unités"
            )

        # ============================
        #   Grille
        # ============================
        output.append("=" * grid_width)
        for row in grid:
            output.append("".join(row))
        output.append("=" * grid_width)

        # ============================
        #   Temps & fin
        # ============================
        output.append(
            f"Temps: {meta['time']:.2f}s / {meta['max_time']:.0f}s"
        )

        if meta["finished"]:
            if meta["winner"]:
                output.append(f"🏆 Vainqueur: {meta['winner']}")
            else:
                output.append("⚖️ Match nul (temps écoulé)")

        print("\n".join(output))

        # Limitation FPS (vue uniquement)
        time.sleep(1 / self.fps)
