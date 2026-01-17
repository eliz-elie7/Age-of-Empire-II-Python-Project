"""
CLI (Command Line Interface) du projet MedievAIl.

Permet de :
 - Lancer un combat entre deux armées
 - Générer un scénario
 - Simuler une bataille complète
"""

from __future__ import annotations
# src/cli.py
import argparse
from src.core.units import UnitType
from src.core.scenario import get_scenario
from src.ai import get_general
from src.vis.terminal_view import TerminalView
from src.core.battle import Battle
import time
import math
import random
FPS = 20
FRAME_DELAY = 1 / FPS



# ============================================================
# CLI arguments parsing
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="Medievail — moteur de bataille"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Lancer une bataille")
    run.add_argument("scenario", type=str)
    run.add_argument("ai_a", type=str)
    run.add_argument("ai_b", type=str)
    run.add_argument("-t", "--terminal", action="store_true")

    plot = sub.add_parser("plot", help="Lancer une expérimentation et tracer")
    plot.add_argument("ai", type=str)
    plot.add_argument("plotter", type=str)
    plot.add_argument("scenario", type=str)
    plot.add_argument("unit_types", type=str)
    plot.add_argument("N_range", type=str)
    plot.add_argument("-N", "--repeats", type=int, default=10)


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

def run_battle(args):
    scenario_fn = get_scenario(args.scenario)

    general_a = get_general(args.ai_a)()
    general_b = get_general(args.ai_b)()

    players, world_map = scenario_fn(UnitType.KNIGHT, 2, general_a, general_b)

    battle = Battle(players=players, world_map=world_map, logic_dt=0.05, max_time=60)

    viewer = TerminalView() if args.terminal else None
    if viewer:
        viewer.on_enter(battle, battle.get_state())

    running = True
    print("🚀 Démarrage du combat...")

    while not battle.finished and running:

        battle.update()
        game_state = battle.get_state()

        if viewer:
            action = viewer.handle_input()
            if action == "quit":
                running = False

            viewer.render(game_state)

        time.sleep(FRAME_DELAY)

    print("Combat terminé")
    if battle.winner:
        print("Vainqueur :", battle.winner.name)
        print_battle_summary(battle)

def run_plot(args):
    from src.core.scenario import run_lanchester_experiment
    from src.core.plot import get_plotter
    from src.core.units import UnitType

    unit_types = [
        UnitType[u.strip().upper()]
        for u in args.unit_types.strip("[]").split(",")
    ]

    try:
        start, end = args.N_range.split(":")
        N_range = range(int(start), int(end))
    except ValueError:
        raise ValueError(
            "Format invalide pour N_range. Utilise start:end (ex: 1:100)"
        )

    data = run_lanchester_experiment(
        general_name=args.ai,
        unit_types=unit_types,
        N_range=N_range,
        repeats=args.repeats
    )

    plotter = get_plotter(args.plotter)
    plotter.plot(data)



def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_battle(args)
    elif args.command == "plot":
        run_plot(args)


    # Résumé final
#    print_battle_summary(battle)

#    return 0


if __name__ == "cli_main":
    main()