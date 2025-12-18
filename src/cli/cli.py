"""
CLI (Command Line Interface) du projet MedievAIl.

Permet de :
 - Lancer un combat entre deux armées
 - Générer un scénario
 - Simuler une bataille complète
"""

from __future__ import annotations
import argparse
import sys
import time

from src.core.scenario import get_scenario
from src.core.battle import Battle
from src.core.map import Map


# ============================================================
# CLI arguments parsing
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="medievail",
        description="MedievAIl — moteur de simulation de batailles médiévales"
    )

    parser.add_argument(
        "--scenario", "-s",
        type=str,
        default="lanchester",
        help="Nom du scénario (lanchester, mirror, skirmish)"
    )

    parser.add_argument(
        "--type", "-t",
        type=str,
        default="balanced",
        help="Type interne du scénario"
    )

    parser.add_argument(
        "--size",
        type=int,
        default=100,
        help="Nombre d’unités par camp"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Affiche la progression du combat"
    )

    parser.add_argument(
        "--logic-dt",
        type=float,
        default=0.05,
        help="Pas de temps logique"
    )

    parser.add_argument(
        "--max-time",
        type=float,
        default=120.0,
        help="Durée max de la bataille (secondes simulées)"
    )

    return parser


# ============================================================
# Affichage des résultats
# ============================================================

def print_battle_summary(battle: Battle):
    print("\n" + "=" * 50)
    print("BATTLE FINISHED")
    print("=" * 50)
    print(f"Simulated time : {battle.time:.2f}s")

    if battle.winner:
        print(f"Winner         : {battle.winner.name}")
        print(f"Remaining units: {len(battle.winner.squad)}")
    else:
        print("Result         : DRAW (time limit reached)")
    print("=" * 50)


# ============================================================
# Exécution principale
# ============================================================

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Récupération du scénario
    try:
        scenario_fn = get_scenario(args.scenario)
    except ValueError as e:
        print(f"Erreur : {e}")
        sys.exit(1)

    # Génération des joueurs
    try:
        playerA, playerB = scenario_fn(args.type, args.size)
    except Exception as e:
        print(f"Erreur scénario : {e}")
        sys.exit(1)

    # Création de la map
    world_map = Map(width=120, height=120)

    # Création de la bataille
    battle = Battle(
        players=[playerA, playerB],
        world_map=world_map,
        logic_dt=args.logic_dt,
        max_time=args.max_time
    )

    # Boucle principale
    while not battle.finished:
        state = battle.update()

        if args.verbose and state:
            print(
                f"t={state['game_time']:.2f}s | "
                + " | ".join(
                    f"{p['name']}:{p['alive_units']}"
                    for p in state["players"]
                )
            )

    # Résumé final
    print_battle_summary(battle)

    return 0


if __name__ == "__main__":
    main()
