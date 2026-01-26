"""
CLI (Command Line Interface) du projet MedievAIl.

Permet de :
 - Lancer un combat entre deux armées
 - Générer un scénario
 - Simuler une bataille complète
"""

import json
from __future__ import annotations
import argparse
from pickle import load
from re import sub
from src.core.scenario import get_scenario
from src.ai import get_general
from src.vis.terminal_view import TerminalView
from src.core.battle import Battle
import time
from src.data.saves.save import load_battle
from itertools import combinations


# ============================================================
# CLI arguments parsing
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="Medievail — moteur de bataille"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    #run
    run = sub.add_parser("run", help="Lancer une bataille")
    run.add_argument("scenario", type=str)
    run.add_argument("ai_a", type=str)
    run.add_argument("ai_b", type=str)
    run.add_argument("-t", "--terminal", action="store_true")

    #load
    load = sub.add_parser("load", help="Charger une bataille sauvegardée")
    load.add_argument("savefile", type=str)
    load.add_argument("-t", "--terminal", action="store_true")

    #tourney
    tourney = sub.add_parser("tourney", help="Lancer un tournoi automatique")
    tourney.add_argument("-G", "--generals", nargs="+", required=True)
    tourney.add_argument("-S", "--scenarios", nargs="+", required=True)
    tourney.add_argument("-N", type=int, default=10)
    tourney.add_argument("-na", action="store_true")
    tourney.add_argument("-d", "--datafile", type=str, required=True)

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

# run_battle
def run_battle(args):
    scenario_fn = get_scenario(args.scenario)

    general_a = get_general(args.ai_a)
    general_b = get_general(args.ai_b)

    players, world_map = scenario_fn(general_a, general_b)

    battle = Battle(players=players, world_map=world_map)

    viewer = TerminalView() if args.terminal else None #GraphicalView() à venir

    while not battle.finished:
        state = battle.update()
        if viewer and state:
            viewer.draw(state, world_map)
        time.sleep(0.04)

    print("Combat terminé")
    if battle.winner:
        print("Vainqueur :", battle.winner.name)
    
    return battle


# tourney
def tourney(args):
    results = []

    for scenario_name in args.scenarios:
        scenario_fn = get_scenario(scenario_name)

        for ai1, ai2 in combinations(args.generals, 2):
            for n in range(args.N):

                # alternance des positions
                if not args.na and n % 2 == 1:
                    a, b = ai2, ai1
                else:
                    a, b = ai1, ai2

                general_a = get_general(a)
                general_b = get_general(b)

                players, world_map = scenario_fn(general_a, general_b)
                battle = Battle(players, world_map)

                start = time.time()
                battle.run()
                duration = time.time() - start

                result = {
                    "scenario": scenario_name,
                    "ai_a": a,
                    "ai_b": b,
                    "round": n,
                    "winner": battle.winner.name if battle.winner else None,
                    "turns": battle.turn,
                    "duration": duration
                }

                results.append(result)

    # Écriture des résultats
    with open(args.datafile, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"Tournoi terminé — résultats écrits dans {args.datafile}")

def run_load(args):
    battle = load_battle(args.savefile)

    viewer = TerminalView() if args.terminal else None #GraphicalView() à venir

    while not battle.finished:
        state = battle.update()
        if viewer and state:
            viewer.draw(state, battle.world_map)
        time.sleep(0.04)

    print("Combat terminé")
    if battle.winner:
        print("Vainqueur :", battle.winner.name)

# main
def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        battle = run_battle(args)
        print_battle_summary(battle)

    elif args.command == "load":
        run_load(args)

    elif args.command == "tourney":
        tourney(args)



if __name__ == "cli_main":
    main()
