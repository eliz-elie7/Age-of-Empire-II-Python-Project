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
from src.core.scenario import get_scenario
from src.ai import get_general
from src.vis.terminal_view import TerminalView
from src.core.battle import Battle
import time
import sys
import subprocess


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

    general_a = get_general(args.ai_a)
    general_b = get_general(args.ai_b)

    players, world_map = scenario_fn(general_a, general_b)

    battle = Battle(players=players, world_map=world_map)

    viewer = TerminalView() if args.terminal else None 
    running = True
    
    while not battle.finished and running:
        # 1. On ne met à jour le combat que si on n'est pas en pause (géré par le flux normal ici)
        battle.update()
        state = battle.get_state()
        
        # 2. Gestion des entrées
        action = viewer.handle_input()
        
        if action == "QUIT":
            running = False
            
        elif action == "p":
            print("\n" + "="*30)
            print("PAUSE ACTIVÉE")
            print("Lancement de html_generator...")
            
            # --- ÉTAPE A : Lancer le script html_generator ---
            try:
                # sys.executable assure qu'on utilise le même interpréteur python (python3, venv, etc.)
                subprocess.run([sys.executable, "html_generator.py"])
                print("Génération terminée.")
            except Exception as e:
                print(f"Erreur lors du lancement du script : {e}")

            print("Appuyez sur 'p' pour reprendre le combat.")
            print("="*30 + "\n")

            # --- ÉTAPE B : Boucle d'attente (Pause) ---
            paused = True
            while paused and running:
                # On continue d'écouter le clavier sans mettre à jour la bataille
                pause_action = viewer.handle_input()
                
                if pause_action == "p":
                    paused = False
                    print(">>> REPRISE DU COMBAT")
                elif pause_action == "QUIT":
                    running = False
                    paused = False
                
                # Petite pause pour ne pas surcharger le processeur
                time.sleep(0.1)

        # 3. Affichage
        if running: # On affiche seulement si on n'a pas quitté
            viewer.render(state)    

        time.sleep(0.04)

    print("Combat terminé")
    if battle.winner:
        print("Vainqueur :", battle.winner.name)

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_battle(args)


    # Résumé final
#    print_battle_summary(battle)

#    return 0


if __name__ == "cli_main":
    main()
