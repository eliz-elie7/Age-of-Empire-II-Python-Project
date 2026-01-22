"""
CLI (Command Line Interface) du projet MedievAIl.
"""

from __future__ import annotations
# src/cli.py
import argparse
from src.core.units import UnitType
from src.core.scenario import get_scenario
from src.ai import get_general
from src.vis.terminal_view import TerminalView
from src.vis.gui_view import IsometricView
from src.core.battle import Battle
import time
import math
import random
import pygame

# --- AJOUT 1 : L'IMPORT ---
from src.data_exporter import save_battle_report 

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
    # Ton argument est déjà là, c'est parfait :
    run.add_argument(
    "-d", "--data",type=str,default=None,help="Chemin du fichier où écrire les données de la bataille")

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

    viewer = TerminalView() if args.terminal else IsometricView()
    if viewer:
        viewer.on_enter(battle, battle.get_state())
    if isinstance(viewer, IsometricView):
        screen = pygame.display.set_mode((1800, 1000))
    
    running = True
    print("🚀 Démarrage du combat...")

    while not battle.finished and running:

        battle.update()
        game_state = battle.get_state()

        action = viewer.handle_input()

        if action == "quit":
            running = False

        elif action == "switch_view":
            viewer.on_exit()

            if isinstance(viewer, TerminalView):
                viewer = IsometricView()
            else:
                viewer = TerminalView()

            viewer.on_enter(battle, game_state)

        # 3️⃣ rendu
        viewer.render(game_state)

        time.sleep(FRAME_DELAY)

    print("Combat terminé")
    if battle.winner:
        print("Vainqueur :", battle.winner.name)
        print_battle_summary(battle)

    # --- AJOUT 2 : SAUVEGARDE SI DEMANDÉ ---
    if args.data:
        save_battle_report(args.data, battle, args)


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

if __name__ == "cli_main":
    main()