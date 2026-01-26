# main.py
from src.cli.cli import main as cli_main

if __name__ == "__main__":
    cli_main()



"""
from src.core.units import create_unit, UnitType
from src.core.battle import Battle
from src.core.player import Player
from src.ai.BrainDead import BrainDead
from src.ai.Daft import Daft
from src.vis.terminal_view import TerminalView
from src.core.map import Map

import time
import random


def spawn_line(player, world_map, existing_units, unit_type, start_x, start_y, count, spacing):
    
    #Génère une ligne d’unités espacées régulièrement.
    #Utilise la map pour repositionner légèrement si collision.
    

    for i in range(count):
        target_x = start_x + i * spacing
        target_y = start_y + random.uniform(-5, 5)  # léger décalage naturel

        # création temporaire
        unit = create_unit(unit_type, target_x, target_y, player)

        # placement final via la carte
        sx, sy = world_map.find_spawn_position(
            unit, target_x, target_y, existing_units,
            max_radius=80, step=4
        )

        unit.x, unit.y = sx, sy
        player.add_unit(unit)
        existing_units.append(unit)


def main():
    print("🎮 Initialisation Medievali...")

    TILE = 32  # pixels par tile (doit correspondre à src/core/units.TILE)
    # === Généraux et joueurs ===
    player_a = Player("Player A", BrainDead())
    player_b = Player("Player B", Daft())

    # === Carte à l'échelle des tiles (larger pour supporter 200+ unités) ===
    MAP_TILES_W = 200
    MAP_TILES_H = 80
    world_map = Map(width=MAP_TILES_W * TILE, height=MAP_TILES_H * TILE, collision_allowance=0.5)

    # === Formation en ligne (espacement en pixels calculé via TILE) ===
    LINE_COUNT = 10          # ex: augmenter pour tests (60 par camp -> 120 unités total)
    LINE_SPACING = int(2.5 * TILE)  # ~80 px comme avant
    LINE_Y = (MAP_TILES_H // 2) * TILE  # ligne verticale de référence au milieu de la carte

    # prototype pour lire la LOS en pixels
    proto = create_unit(UnitType.KNIGHT, 0, 0, player_a)
    knight_los = proto.get_line_of_sight()
    desired_gap = max(int(knight_los * 1.2), int(6 * TILE))

    mid_x = world_map.get_width() / 2.0
    half_formation_width = ((LINE_COUNT - 1) * LINE_SPACING) / 2.0
    left_center = mid_x - (desired_gap / 2.0)
    right_center = mid_x + (desired_gap / 2.0)
    left_start_x = left_center - half_formation_width
    right_start_x = right_center - half_formation_width

    all_units = []

    spawn_line(
        player_a, world_map, all_units,
        UnitType.KNIGHT,
        start_x=left_start_x,
        start_y=LINE_Y,
        count=LINE_COUNT,
        spacing=LINE_SPACING
    )

    spawn_line(
        player_b, world_map, all_units,
        UnitType.KNIGHT,
        start_x=right_start_x,
        start_y=LINE_Y,
        count=LINE_COUNT,
        spacing=LINE_SPACING
    )

    # === Combat ===
    battle = Battle(
        players=[player_a, player_b],
        world_map=world_map,
        logic_dt=0.05,
        max_time=240
    )

    viewer = TerminalView(fps=25)

    print("🚀 Démarrage du combat...")

    while not battle.finished and viewer.is_running():
        state = battle.update()
        if state:
            viewer.draw(state, world_map)
        time.sleep(1 / viewer.fps)

    print("⚔️ Combat terminé !")
    if battle.winner:
        print(f"🏆 Vainqueur: {battle.winner.name}")
    else:
        print("⏸️ Temps écoulé.")


if __name__ == "__main__":
    main()
"""