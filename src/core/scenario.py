# medievail/core/scenario.py

"""
scenario.py — Génération de scénarios programmatiques pour les simulations.
Contient des fonctions utilitaires pour construire des armées complètes
(Player + unités) selon différents modèles : Lanchester, mirroring, skirmish…

Aucune dépendance à l'affichage ou au CLI.
"""

from __future__ import annotations
from typing import List, Tuple, Callable
import random

from .player import Player
from .unit import Knight, Pikeman, Archer, Unit
from .general import BrainDeadGeneral


# ============================================================
# Helpers internes
# ============================================================

UNIT_TYPES = {
    "knight": Knight,
    "pikeman": Pikeman,
    "archer": Archer,
}


def _make_army(unit_list: List[Unit], name: str = "Army") -> Player:
    """Construit une armée (Player) avec un général trivial."""
    general = BrainDeadGeneral()   # par défaut, IA simple
    return Player(name=name, general=general, units=unit_list)


# ============================================================
# GÉNÉRATEUR : Lanchester
# ============================================================

def Lanchester(type: str = "balanced", N: int = 100) -> Tuple[Player, Player]:
    """
    Génère deux armées suivant des ratios inspirés des équations de Lanchester.

    Args:
        type: "balanced", "skewed", "archers", "cavalry"
        N: taille totale (par armée)

    Retourne:
        (Player A, Player B)
    """

    if type not in ("balanced", "skewed", "archers", "cavalry"):
        raise ValueError(f"Unknown Lanchester type: {type}")

    if type == "balanced":
        comp = {"knight": 0.33, "pikeman": 0.33, "archer": 0.34}

    elif type == "skewed":
        comp = {"knight": 0.60, "pikeman": 0.25, "archer": 0.15}

    elif type == "archers":
        comp = {"knight": 0.10, "pikeman": 0.20, "archer": 0.70}

    elif type == "cavalry":
        comp = {"knight": 0.75, "pikeman": 0.15, "archer": 0.10}

    # Construire deux armées identiques (cas courant Lanchester)
    def build_one():
        units = []
        for uname, ratio in comp.items():
            count = max(1, int(N * ratio))
            cls = UNIT_TYPES[uname]
            for _ in range(count):
                units.append(cls())
        random.shuffle(units)
        return units

    army_A = _make_army(build_one(), "Lanchester A")
    army_B = _make_army(build_one(), "Lanchester B")

    return army_A, army_B


# ============================================================
# GÉNÉRATEUR : Mirroring (perf tests)
# ============================================================

def mirror(unit: Unit, N: int = 50) -> Tuple[Player, Player]:
    """
    Génère un test symétrique basé sur un seul type d'unité.
    Pratique pour les benchmarks d’IA/collisions.
    """

    units_A = [unit.clone() for _ in range(N)]
    units_B = [unit.clone() for _ in range(N)]

    return (
        _make_army(units_A, f"Mirror {unit.name} A"),
        _make_army(units_B, f"Mirror {unit.name} B"),
    )


# ============================================================
# GÉNÉRATEUR : Skirmish Aléatoire
# ============================================================

def skirmish(N: int = 100) -> Tuple[Player, Player]:
    """
    Génère un affrontement aléatoire, composition totale N par camp.

    Ratio purement aléatoire mais uniforme entre les types.
    """

    def build_one():
        units = []
        for _ in range(N):
            cls = random.choice(list(UNIT_TYPES.values()))
            units.append(cls())
        return units

    return (
        _make_army(build_one(), "Skirmish A"),
        _make_army(build_one(), "Skirmish B"),
    )


# ============================================================
# API publique
# ============================================================

SCENARIOS: dict[str, Callable] = {
    "lanchester": Lanchester,
    "mirror": mirror,
    "skirmish": skirmish,
}

def get_scenario(name: str) -> Callable:
    """
    Récupère un constructeur de scénario par nom (utilisé par le CLI).

    Exemple :
        func = get_scenario("lanchester")
        armyA, armyB = func("balanced", 200)
    """
    key = name.lower()
    if key not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}")
    return SCENARIOS[key]

