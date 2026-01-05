"""
scenario.py
-----------
Génération des scénarios de bataille.

Un scénario :
- reçoit (type, size)
- retourne (playerA, playerB)

Aucune logique de combat ici.
"""

from typing import Callable, Tuple

from src.core.player import Player
from src.core.map import Map
from src.core.units import create_unit, UnitType

TILE = 32  # pixels par tile (doit correspondre à src/core/units.TILE)
DEFAULT_SIZE = 15  # taille par défaut des armées

# ============================================================
# Helpers
# ============================================================

def build_player(name: str, general, size: int, unit_type, start_x, start_y, spacing, world_map):
    player = Player(name, general)
    units = []

    for i in range(size):
        x = start_x + i * spacing
        y = start_y
        unit = create_unit(unit_type, x, y, player)
        player.add_unit(unit)
        units.append(unit)

    return player, units


# ============================================================
# SCÉNARIOS LANCHESTER
# ============================================================

def lanchester_scenario(general_a, general_b):
    player_a = Player("Army A", general_a)
    player_b = Player("Army B", general_b)

    MAP_W = 120 * TILE
    MAP_H = 60 * TILE
    world_map = Map(MAP_W, MAP_H)

    size = 20  # taille par camp (fixe pour l’instant, OK pour l’énoncé)

    mid_y = MAP_H // 2
    left_x = MAP_W * 0.25
    right_x = MAP_W * 0.75

    for i in range(size):
        u1 = create_unit(UnitType.KNIGHT, left_x, mid_y + i * 2, player_a)
        u2 = create_unit(UnitType.KNIGHT, right_x, mid_y + i * 2, player_b)
        player_a.add_unit(u1)
        player_b.add_unit(u2)

    return [player_a, player_b], world_map


# ============================================================
# AUTRES SCÉNARIOS
# ============================================================

def skirmish_scenario(general_a, general_b):
    """
    Combat désorganisé : unités réparties aléatoirement
    """
    import random

    player_a = Player("Army A", general_a)
    player_b = Player("Army B", general_b)

    world_map = Map(120 * TILE, 80 * TILE)

    for _ in range(DEFAULT_SIZE):
        x = random.uniform(10 * TILE, 50 * TILE)
        y = random.uniform(10 * TILE, 70 * TILE)
        player_a.add_unit(create_unit(UnitType.KNIGHT, x, y, player_a))

        x = random.uniform(70 * TILE, 110 * TILE)
        y = random.uniform(10 * TILE, 70 * TILE)
        player_b.add_unit(create_unit(UnitType.KNIGHT, x, y, player_b))

    return [player_a, player_b], world_map


def mirror_scenario(general_a, general_b):
    """
    Deux armées strictement symétriques
    """
    player_a = Player("Army A", general_a)
    player_b = Player("Army B", general_b)

    world_map = Map(120 * TILE, 60 * TILE)

    mid_y = world_map.get_height() / 2

    for i in range(DEFAULT_SIZE):
        y = mid_y + (i - DEFAULT_SIZE / 2) * TILE
        player_a.add_unit(create_unit(UnitType.KNIGHT, 30 * TILE, y, player_a))
        player_b.add_unit(create_unit(UnitType.KNIGHT, 90 * TILE, y, player_b))

    return [player_a, player_b], world_map


# ============================================================
# REGISTRY
# ============================================================

SCENARIOS = {
    "lanchester": lanchester_scenario,
    "mirror": mirror_scenario,
    "skirmish": skirmish_scenario,
}


_SCENARIOS = {
    "lanchester": lanchester_scenario,
}

def get_scenario(name):
    try:
        return SCENARIOS[name.lower()]
    except KeyError:
        raise ValueError(f"Scénario inconnu : {name}")

