"""
CLI (Command Line Interface) du projet MedievAIl.
"""
from __future__ import annotations
import argparse
import time
import pygame

# --- Imports du Moteur ---
from src.core.units import UnitType
from src.core.scenario import get_scenario
from src.ai import get_general

from src.core.battle import Battle

# --- Imports Visuels ---
from src.vis.terminal_view import TerminalView
from src.vis.gui_view import IsometricView

# --- LES 3 FICHIERS HTML ---
from src.fichiers.html_generator import generate_snapshot_html  # 1. HUD Tactique (TAB)
from src.fichiers.data_exporter import save_battle_report            # 2. Export Données (-d)
from src.fichiers.history import add_fight_history              # 3. Historique (Auto)
from src.fichiers.tournament_report import generate_tournament_report






FPS = 20
FRAME_DELAY = 1 / FPS

# ============================================================
# 1. ARGUMENTS
# ============================================================
def build_parser():
    parser = argparse.ArgumentParser(description="Medievail — moteur de bataille")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Lancer une bataille")
    run.add_argument("scenario", type=str)
    run.add_argument("ai_a", type=str)
    run.add_argument("ai_b", type=str)
    run.add_argument("-t", "--terminal", action="store_true")
    # Argument pour l'export HTML (-d)
    run.add_argument("-d", "--data", type=str, default=None, help="Fichier de sortie des données")

    # ... (Arguments pour plot, inchangés) ...
    plot = sub.add_parser("plot", help="Lancer une expérimentation")
    plot.add_argument("ai", type=str)
    plot.add_argument("plotter", type=str)
    plot.add_argument("scenario", type=str)
    plot.add_argument("unit_types", type=str)
    plot.add_argument("N_range", type=str)
    plot.add_argument("-N", "--repeats", type=int, default=10)

    #load
    load = sub.add_parser("load", help="Charger une bataille sauvegardÃ©e")
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
# 2. AFFICHAGE CONSOLE
# ============================================================
def print_battle_summary(battle: Battle):
    print("\n" + "=" * 50)
    print("BATAILLE TERMINÉE")
    print("=" * 50)
    print(f"Temps simulé : {battle.time:.2f}s")
    if battle.winner:
        print(f"Vainqueur      : {battle.winner.name}")
        print(f"Unités restantes: {len(battle.winner.squad)}")
    else:
        print("Résultat       : ÉGALITÉ")
    print("=" * 50)

# ============================================================
# 3. EXÉCUTION (RUN)
# ============================================================
def run_battle(args):
    # --- Chargement ---
    scenario_fn = get_scenario(args.scenario)
    general_a = get_general(args.ai_a) # Pas de parenthèses !
    general_b = get_general(args.ai_b) # Pas de parenthèses !

    # --- Création de la bataille (VERSION ROBUSTE) ---
    # C'est ICI que ça change pour éviter le bug Lanchester
    try:
        # Tentative 1 : Scénario complexe (ex: Lanchester) -> 4 arguments
        players, world_map = scenario_fn(UnitType.KNIGHT, 10, general_a, general_b)
    except TypeError:
        # Tentative 2 : Scénario simple (ex: map1, random) -> 2 arguments
        players, world_map = scenario_fn(general_a, general_b)
    
    # IMPORTANT : On compte les unités au début pour l'historique
    start_count_a = len(players[0].squad)
    start_count_b = len(players[1].squad)

    battle = Battle(players=players, world_map=world_map, logic_dt=0.05, max_time=120)

    # --- Initialisation Vue ---
    viewer = TerminalView() if args.terminal else IsometricView()
    if viewer:
        viewer.on_enter(battle, battle.get_state())
    if isinstance(viewer, IsometricView):
        pygame.display.set_mode((1800, 1000))
    
    running = True
    print(f"🚀 Démarrage : {players[0].name} vs {players[1].name}")
    print("👉 Appuyez sur [TAB] pour le HUD Tactique.")

    # --- BOUCLE PRINCIPALE ---
    while not battle.finished and running:
        battle.update()
        game_state = battle.get_state()
        
        # Gestion des Inputs
        action = viewer.handle_input()

        if action == "quit":
            running = False

        elif action == "switch_view":
            viewer.on_exit()
            viewer = IsometricView() if isinstance(viewer, TerminalView) else TerminalView()
            viewer.on_enter(battle, game_state)
            
        # --- HTML 1 : HUD TACTIQUE (Touche TAB) ---
        elif action == "\t": # Touche TAB renvoyée par la vue
            print("\n⏸  PAUSE TACTIQUE")
            time.sleep(0.3)
            try:
                generate_snapshot_html(battle.players, battle.time)
            except Exception as e:
                print(f"⚠️ Erreur HUD : {e}")
            
            # Boucle de pause
            paused = True
            while paused and running:
                if isinstance(viewer, IsometricView):
                    viewer.render(game_state)
                    # Petit tick pour ne pas bloquer l'OS
                    pygame.event.pump() 
                
                pause_act = viewer.handle_input()
                if pause_act == "\t": paused = False
                elif pause_act == "quit": running = False; paused = False
                
                if not isinstance(viewer, IsometricView):
                    time.sleep(0.1)
        # --- GESTION SAUVEGARDE (F11) ---
        elif action == "save":
            battle.save_state()  # Appelle la méthode qu'on a créée dans Battle
            time.sleep(0.2)      # Petit délai pour éviter de sauvegarder 10 fois par seconde

        # --- GESTION CHARGEMENT (F12) ---
        elif action == "load":
            loaded_battle = Battle.load_state() # Charge le fichier
            
            if loaded_battle:
                # REMPLACEMENT CRITIQUE : L'ancienne bataille est écrasée par la nouvelle
                battle = loaded_battle 
                
                # IMPORTANT : On dit à la vue de se mettre à jour avec la nouvelle bataille
                if viewer:
                    viewer.on_enter(battle, battle.get_state())
                
                time.sleep(0.2)


        # Rendu normal
        viewer.render(game_state)
        time.sleep(FRAME_DELAY)

    # --- FIN DU COMBAT ---
    print_battle_summary(battle)

    # --- HTML 2 : EXPORT DONNÉES (-d) ---
    if args.data:
        save_battle_report(args.data, battle, args)

    # --- HTML 3 : HISTORIQUE AUTOMATIQUE ---
    winner_name = battle.winner.name if battle.winner else "DRAW"
    survivors_data = []
    for p in battle.players:
        for u in p.squad:
            if u.is_alive:
                sym = u.get_symbol() if hasattr(u, "get_symbol") else "U"
                survivors_data.append((sym, p.name))
    
    try:
        add_fight_history(
            p1_name=players[0].name,
            p2_name=players[1].name,
            ia1=args.ai_a,
            ia2=args.ai_b,
            u1_start=start_count_a,
            u2_start=start_count_b,
            winner=winner_name,
            duration=battle.time,
            survivors_data=survivors_data
        )
        print("📜 Historique mis à jour (history.html)")
    except Exception as e:
        print(f"⚠️ Erreur Historique : {e}")

from itertools import product
import json

def tourney(args):
    results = []
    
    # --- 1. Initialisation ---
    stats = {}
    for sc in args.scenarios:
        stats[sc] = {}
        for g1 in args.generals:
            stats[sc][g1] = {}
            for g2 in args.generals:
                stats[sc][g1][g2] = {'wins': 0, 'matches': 0}

    print(f"⚔️  Démarrage du tournoi : {len(args.generals)} Généraux sur {len(args.scenarios)} Scénarios")

    # --- 2. Boucle du Tournoi ---
    for scenario_name in args.scenarios:
        scenario_fn = get_scenario(scenario_name)

        for ai1, ai2 in product(args.generals, repeat=2):
            for n in range(args.N):

                # Gestion de l'inversion (Player 1 vs Player 2)
                if not args.na and n % 2 == 1:
                    a, b = ai2, ai1 
                else:
                    a, b = ai1, ai2

                general_a = get_general(a)
                general_b = get_general(b)

                # players[0] est piloté par 'a', players[1] par 'b'
                players, world_map = scenario_fn(UnitType.KNIGHT, 5, general_a, general_b)
                battle = Battle(players, world_map)

                battle_result = battle.run()

                # --- 3. DÉTECTION ROBUSTE DU VAINQUEUR ---
                # On regarde quel OBJET Player a gagné, pas son nom.
                actual_winner_ai_name = None
                
                if battle.winner == players[0]:
                    actual_winner_ai_name = a  # C'est l'IA 'a' qui a gagné
                elif battle.winner == players[1]:
                    actual_winner_ai_name = b  # C'est l'IA 'b' qui a gagné
                
                # Enregistrement brut (JSON)
                result = {
                    "scenario": scenario_name,
                    "ai_a": a,
                    "ai_b": b,
                    "round": n,
                    "winner": actual_winner_ai_name, # On stocke le nom de l'IA, pas "Player 1"
                    "turns": battle_result.turns,
                    "duration": battle_result.duration,
                    "remaining_units": battle_result.remaining_units,
                }
                results.append(result)

                # --- 4. Aggregation pour le HTML ---
                # Ici ai1 est la "ligne" du tableau, ai2 la "colonne"
                stats[scenario_name][ai1][ai2]['matches'] += 1
                
                if actual_winner_ai_name == ai1:
                    stats[scenario_name][ai1][ai2]['wins'] += 1
                
                print(".", end="", flush=True)

    print("\n✅ Tournoi terminé.")

    # --- 5. Export JSON ---
    with open(args.datafile, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    # --- 6. Génération HTML ---
    try:
        generate_tournament_report(stats, args.generals, args.scenarios)
    except Exception as e:
        print(f"❌ Erreur HTML : {e}")

# ============================================================
def run_plot(args):
    from src.core.scenario import run_lanchester_experiment
    from src.core.plot import get_plotter
    
    unit_types = [UnitType[u.strip().upper()] for u in args.unit_types.strip("[]").split(",")]
    start, end = args.N_range.split(":")
    N_range = range(int(start), int(end))

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
    elif args.command == "tourney":
        tourney(args)

if __name__ == "cli_main":
    main()