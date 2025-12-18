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
from src.core.units import Unit


# ============================================================
# Helpers
# ============================================================

def build_player(name: str, size: int, power: float) -> Player:
    """
    Construit un joueur avec une armée homogène.
    """
    player = Player(name=name)

    for _ in range(size):
        unit = Unit(power=power)
        player.add_unit(unit)

    return player


# ============================================================
# SCÉNARIOS LANCHESTER
# ============================================================

def lanchester_scenario(kind: str, size: int) -> Tuple[Player, Player]:
    """
    Scénarios inspirés de Lanchester.
    """
    if kind == "balanced":
        a = build_player("A", size, power=1.0)
        b = build_player("B", size, power=1.0)

    elif kind == "numerical":
        a = build_player("A", size, power=1.0)
        b = build_player("B", size * 2, power=1.0)

    elif kind == "technological":
        a = build_player("A", int(size * 0.7), power=2.0)
        b = build_player("B", size, power=1.0)

    else:
        raise ValueError(f"Type de scénario Lanchester inconnu : {kind}")

    return a, b


# ============================================================
# AUTRES SCÉNARIOS
# ============================================================

def mirror_scenario(kind: str, size: int) -> Tuple[Player, Player]:
    """
    Deux camps strictement identiques.
    """
    a = build_player("A", size, power=1.2)
    b = build_player("B", size, power=1.2)
    return a, b


def skirmish_scenario(kind: str, size: int) -> Tuple[Player, Player]:
    """
    Escarmouche : peu d’unités, forte puissance.
    """
    a = build_player("A", size // 2, power=1.5)
    b = build_player("B", size // 2, power=1.5)
    return a, b


# ============================================================
# REGISTRY
# ============================================================

_SCENARIOS = {
    "lanchester": lanchester_scenario,
    "mirror": mirror_scenario,
    "skirmish": skirmish_scenario,
}


def get_scenario(name: str) -> Callable[[str, int], Tuple[Player, Player]]:
    """
    Retourne la fonction scénario associée à un nom.
    """
    try:
        return _SCENARIOS[name]
    except KeyError:
        raise ValueError(
            f"Scénario inconnu : {name} "
            f"(disponibles : {', '.join(_SCENARIOS.keys())})"
        )
