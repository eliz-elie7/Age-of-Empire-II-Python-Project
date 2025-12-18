import os
import math
import time
from typing import Dict, Any


class TerminalView:
    """Affichage propre et stable dans le terminal."""

    def __init__(self, fps: int = 25):
        self.fps = fps
        self._running = True

        # Forcer clear chaque frame
        self.last_clear_time = 0
        self.clear_interval = 0.0

        # 1 caractère = TILE pixels (aligné avec units.TILE). Choisi ici en dur pour éviter imports circulaires.
        self.grid_size_factor = 32.0

        self.min_width = 80
        self.min_height = 20

    def is_running(self) -> bool:
        return self._running

    def _clear_screen(self):
        # Forcer l'effacement à chaque appel pour éviter affichages multiples entre clears
        os.system('cls' if os.name == 'nt' else 'clear')
        self.last_clear_time = time.time()

    def draw(self, state: Dict[str, Any], world_map):
        if not self._running:
            return

        self._clear_screen()

        width_map = world_map.get_width()
        height_map = world_map.get_height()

        grid_width = max(self.min_width, math.ceil(width_map / self.grid_size_factor))
        grid_height = max(self.min_height, math.ceil(height_map / self.grid_size_factor))

        # Grille vide
        grid = [['.' for _ in range(grid_width)] for _ in range(grid_height)]

        # ============================
        #   Placement des unités
        # ============================
        for player in state["players"]:
            for unit in player["units"]:
                gx = int(unit["x"] / self.grid_size_factor)
                gy = int(unit["y"] / self.grid_size_factor)

                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    initial = player["name"][0]
                    grid[gy][gx] = f"{initial}:{unit['symbol']}"

        output = []
        output.append("📊 STATS:")

        for player in state["players"]:
            output.append(f"  {player['name']}: {player['alive_units']} unités vivantes")

            for unit in player["units"]:
                output.append(
                    f"    {unit['symbol']} @ ({unit['x']:.1f}, {unit['y']:.1f}) "
                    f"HP:{unit['hp']}  Ordre:{unit['order']}"
                )

        output.append("=" * grid_width)

        for row in grid:
            output.append(" ".join(row))

        output.append("=" * grid_width)

        output.append(f"🕰️ Temps: {state['game_time']:.2f}s / {state['total_time']:.0f}s")

        if state["finished"]:
            output.append(f"🏆 Vainqueur: {state['winner']}")

        print("\n".join(output))
