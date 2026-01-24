"""
scenario.py
-----------
Génération des scénarios de bataille.

Un scénario :
- crée la map
- crée les joueurs
- place les unités (placement valide, sans superposition)
- retourne ([players], world_map)

Aucune logique de combat ici.
"""

from typing import List, Tuple

from src.core.player import Player
from src.core.map import Map
from src.core.units import create_unit, UnitType

TILE = 32
DEFAULT_SIZE = 15


# ============================================================
# HELPERS DE PLACEMENT
# ============================================================

def spawn_unit_safe(unit_type, x, y, player, world_map, all_units):
    """
    Crée une unité et demande à la map une position valide
    (anti-collision + bords de map)
    """
    # 1) Créer l’unité (temporairement à la position désirée)
    unit = create_unit(unit_type, x, y, player)

    # 2) Demander à la map une position valide
    x, y = world_map.find_spawn_position(
        unit,
        x,
        y,
        all_units
    )

    # 3) Appliquer la position finale
    unit.x = x
    unit.y = y

    # 4) Enregistrer l’unité
    player.add_unit(unit)
    all_units.append(unit)

    return unit



def spawn_line(player, world_map, all_units,
               unit_type, start_x, y, count, spacing):
    """
    Spawn une ligne horizontale d’unités
    """
    for i in range(count):
        x = start_x + i * spacing
        spawn_unit_safe(
            unit_type, x, y,
            player, world_map, all_units
        )


def spawn_square(player, world_map, all_units,
                 unit_type, start_x, start_y,
                 rows, cols, spacing):
    """
    Spawn une formation en carré
    """
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * spacing
            y = start_y + r * spacing
            spawn_unit_safe(
                unit_type, x, y,
                player, world_map, all_units
            )


# ============================================================
# SCÉNARIOS
# ============================================================

import math

def lanchester_scenario(unit_type, N, general_a, general_b):
    """
    Scénario Lanchester(type, N) avec formations carrées
    - Armée A : N unités
    - Armée B : 2N unités
    - Même type
    - Combat immédiat
    """

    player_a = Player("Army A", general_a)
    player_a.color = "Blue"
    player_b = Player("Army B", general_b)
    player_b.color = "Red"

    world_map = Map(width = 120 * TILE, height = 120 * TILE,collision_allowance=0.2)
    all_units = []

    SPACING = int(1.5 * TILE)

    # Prototype pour récupérer la portée réelle
    proto = create_unit(unit_type, 0, 0, player_a)
    attack_range = proto.get_line_of_sight()

    # Gap volontairement faible → combat immédiat
    gap = attack_range * 0.8

    mid_x = world_map.get_width() / 2
    mid_y = world_map.get_height() / 2

    # ==========================
    # Armée A : N unités
    # ==========================
    rows_a = int(math.sqrt(N))
    cols_a = math.ceil(N / rows_a)

    width_a = (cols_a - 1) * SPACING
    height_a = (rows_a - 1) * SPACING

    start_x_a = (mid_x - gap / 2) - width_a
    start_y_a = mid_y - height_a / 2

    spawn_square(
        player_a,
        world_map,
        all_units,
        unit_type,
        start_x_a,
        start_y_a,
        rows_a,
        cols_a,
        SPACING
    )

    # ==========================
    # Armée B : 2N unités
    # ==========================
    Nb = 2 * N
    rows_b = int(math.sqrt(Nb))
    cols_b = math.ceil(Nb / rows_b)

    width_b = (cols_b - 1) * SPACING
    height_b = (rows_b - 1) * SPACING

    start_x_b = (mid_x + gap / 2)
    start_y_b = mid_y - height_b / 2

    spawn_square(
        player_b,
        world_map,
        all_units,
        unit_type,
        start_x_b,
        start_y_b,
        rows_b,
        cols_b,
        SPACING
    )

    return [player_a, player_b], world_map



def mirror_scenario(unit_type , N, general_a, general_b):
   
    player_a = Player("Army A", general_a)
    player_a.color = "Blue"
    player_b = Player("Army B", general_b)
    player_b.color = "Red"

    world_map = Map(width = 120 * TILE, height = 120 * TILE,collision_allowance=0.5)
    all_units = []

    SPACING = int(1.5 * TILE)

    # Prototype pour récupérer la portée réelle
    proto = create_unit(unit_type, 0, 0, player_a)
    attack_range = proto.get_line_of_sight()

    # Gap volontairement faible → combat immédiat
    gap = attack_range * 0.8

    mid_x = world_map.get_width() / 2
    mid_y = world_map.get_height() / 2

    rows_a = int(math.sqrt(N))
    cols_a = math.ceil(N / rows_a)

    width_a = (cols_a - 1) * SPACING
    height_a = (rows_a - 1) * SPACING

    start_x_a = (mid_x - gap / 2) - width_a
    start_y_a = mid_y - height_a / 2

    spawn_square(
        player_a,
        world_map,
        all_units,
        unit_type,
        start_x_a,
        start_y_a,
        rows_a,
        cols_a,
        SPACING
    )

    Nb = N
    rows_b = int(math.sqrt(Nb))
    cols_b = math.ceil(Nb / rows_b)

    width_b = (cols_b - 1) * SPACING
    height_b = (rows_b - 1) * SPACING

    start_x_b = (mid_x + gap / 2)
    start_y_b = mid_y - height_b / 2

    spawn_square(
        player_b,
        world_map,
        all_units,
        unit_type,
        start_x_b,
        start_y_b,
        rows_b,
        cols_b,
        SPACING
    )

    return [player_a, player_b], world_map


def skirmish_scenario(unit_type, N, general_a, general_b):
    """
    Combat désorganisé : unités réparties aléatoirement
    """
    import random

    player_a = Player("Army A", general_a)
    player_b = Player("Army B", general_b)

    world_map = Map(120 * TILE, 80 * TILE)

    all_units = []

    for _ in range(N):
        # Army A (un peu plus à droite)
        spawn_unit_safe(
            unit_type,
            random.uniform(40 * TILE, 55 * TILE),
            random.uniform(10 * TILE, 70 * TILE),
            player_a, world_map, all_units
        )

        # Army B (un peu plus à gauche)
        spawn_unit_safe(
            unit_type,
            random.uniform(65 * TILE, 80 * TILE),
            random.uniform(10 * TILE, 70 * TILE),
            player_b, world_map, all_units
        )

    return [player_a, player_b], world_map


# ============================================================
# REGISTRY
# ============================================================

SCENARIOS = {
    "lanchester": lanchester_scenario,
    "mirror": mirror_scenario,
    "skirmish": skirmish_scenario,
}


def get_scenario(name: str):
    try:
        return SCENARIOS[name.lower()]
    except KeyError:
        raise ValueError(f"Scénario inconnu : {name}")
# ============================================================
# EXPÉRIMENTATIONS (Lanchester)
# ============================================================

from src.core.battle import Battle


def run_lanchester_experiment(
    general_name: str,
    unit_types: list,
    N_range: range,
    repeats: int = 30
):
    from src.ai import get_general

    data = {}  # data[unit_type][N] = list of losses_of_winner

    for unit_type in unit_types:
        data[unit_type] = {}

        for N in N_range:
            data[unit_type][N] = []

            for _ in range(repeats):
                general = get_general(general_name)

                players, world_map = lanchester_scenario(
                    unit_type, N, general, general
                )

                battle = Battle(players, world_map)

                while not battle.finished:
                    battle.update()

                if not battle.winner:
                    continue

                # 🔹 pertes du GAGNANT UNIQUEMENT
                total_hp_lost = sum(
                    u.max_hp - max(u.current_hp, 0)
                    for u in battle.winner.squad
                )
                data[unit_type][N].append(total_hp_lost)
                # print( f"N={N} | winner={battle.winner.name} | "f"total_hp_lost={total_hp_lost}")

    return data
