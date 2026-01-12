"""
CLI (Command Line Interface) du projet MedievAIl.
"""
from __future__ import annotations
import argparse
import time
import sys

# --- IMPORTS ---
from src.core.scenario import get_scenario
from src.ai import get_general
from src.vis.terminal_view import TerminalView
from src.core.battle import Battle

# On importe ta fonction qui génère ET ouvre le fichier
from src.core.html_generator import generate_snapshot_html
from src.core.history import add_fight_history, init_history_file

# ============================================================
# ARGS
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(description="Medievail")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Lancer une bataille")
    run.add_argument("scenario", type=str)
    run.add_argument("ai_a", type=str)
    run.add_argument("ai_b", type=str)
    run.add_argument("-t", "--terminal", action="store_true")
    return parser

# ============================================================
# EXECUTION PRINCIPALE
# ============================================================

def run_battle(args):
    # 1. Setup
    scenario_fn = get_scenario(args.scenario)
    general_a = get_general(args.ai_a)
    general_b = get_general(args.ai_b)
    players, world_map = scenario_fn(general_a, general_b)
    battle = Battle(players=players, world_map=world_map)
    start_counts = {p.name: len(p.squad) for p in players}

    viewer = TerminalView() if args.terminal else None 
    running = True
    
    print(f"⚔️  DÉBUT : {players[0].name} vs {players[1].name}")
    print("👉 Appuyez sur [TAB] pour voir le HUD Tactique.")

    while not battle.finished and running:
        # A. Update
        battle.update()
        state = battle.get_state()
        
        # B. Gestion des entrées
        action = None
        if viewer:
            action = viewer.handle_input()
        
        if action == "QUIT":
            running = False
            
        # --- C'EST ICI QUE CA SE PASSE : TOUCHE TAB ---
        elif action == "\t": 
            print("\n" + "="*40)
            print("⏸  PAUSE TACTIQUE ACTIVÉE")
            
            # 1. On lance ta fonction (Génère + Ouvre le navigateur)
            try:
                print("Génération et ouverture du HUD...")
                generate_snapshot_html(battle.players, battle.time)
            except Exception as e:
                print(f"⚠️ Erreur : {e}")

            print("--> Jeu en pause. Appuyez sur [TAB] pour reprendre.")
            print("="*40 + "\n")

            # 2. Boucle de pause (on bloque ici tant qu'on ne re-clique pas sur TAB)
            paused = True
            while paused and running:
                if viewer:
                    # On écoute le clavier
                    pause_act = viewer.handle_input()
                    
                    # Si on appuie encore sur TAB, on sort de la boucle
                    if pause_act == "\t": 
                        paused = False
                        print("▶️  REPRISE DU COMBAT")
                    elif pause_act == "QUIT": 
                        running = False
                        paused = False
                
                # Petite attente pour ne pas surcharger le CPU pendant la pause
                time.sleep(0.1)

        # C. Affichage
        if running and viewer:
            viewer.render(state)    

        time.sleep(0.04)

    # --- FIN DU COMBAT ---
    print("\nCombat terminé !")
    winner_name = battle.winner.name if battle.winner else "DRAW"
    
    # Gestion de l'historique (inchangé)
    survivors_data = []
    for p in battle.players:
        for u in p.squad:
            if u.current_hp > 0:
                survivors_data.append((u.get_symbol(), p.name))
    
    try:
        with open("history.html", "r") as f: pass
    except FileNotFoundError:
        init_history_file()

    try:
        add_fight_history(players[0].name, players[1].name, args.ai_a, args.ai_b, 
                          start_counts[players[0].name], start_counts[players[1].name], 
                          winner_name, battle.time, survivors_data)
        print("📜 Rapport ajouté à l'historique.")
    except Exception:
        pass

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        run_battle(args)

if __name__ == "cli_main":
    main()