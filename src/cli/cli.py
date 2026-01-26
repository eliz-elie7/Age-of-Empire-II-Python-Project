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
from src.core.scenario import SCENARIO_CONFIG
from src.ai import get_general

from src.core.battle import Battle

# --- Imports Visuels ---
from src.vis.terminal_view import TerminalView
from src.vis.gui_view import IsometricView

# --- LES 3 FICHIERS HTML ---
from src.fichiers.html_generator import generate_snapshot_html  # 1. HUD Tactique (TAB)
from src.fichiers.data_exporter import save_battle_report            # 2. Export Données (-d)
from src.fichiers.history import add_fight_history              # 3. Historique (Auto)
from src.fichiers.tournament_report import generate_tournament_report # Tournoi HTML





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
    # 1. On récupère la config du scénario choisi
    config = SCENARIO_CONFIG.get(args.scenario)
    if not config:
        raise ValueError(f"Scénario inconnu : {args.scenario}")

    scenario_fn = config["fn"]
    # On récupère les arguments spécifiques au scénario (ex: [UnitType, N])
    extra_params = config.get("args", [])

    # 2. On instancie les IA
    general_a = get_general(args.ai_a)
    general_b = get_general(args.ai_b)

    # 3. APPEL GÉNÉRALISÉ
    # On déballe les paramètres spécifiques, puis on ajoute les généraux
    # Signature finale : scenario_fn(param1, param2, ..., general_a, general_b)
    try:
        players, world_map = scenario_fn(*extra_params, general_a, general_b)
    except Exception as e:
        print(f"Erreur lors du lancement du scénario {args.scenario}: {e}")
        return
    
    start_count_a = len(players[0].squad)
    start_count_b = len(players[1].squad)

    # Création de l'objet Battle
    battle = Battle(players=players, world_map=world_map, logic_dt=0.05, max_time=120)

    # --- 2. Initialisation de la Vue ---
    viewer = TerminalView() if args.terminal else IsometricView()
    if viewer:
        viewer.on_enter(battle, battle.get_state())
    
    # --- 3. État du Contrôleur (Flags) ---
    running = True
    is_paused = False
    current_speed = 1  # Vitesse de simulation initiale
    
    print(f"🚀 Démarrage : {players[0].name} vs {players[1].name}")
    print("👉 COMMANDES : [TAB] Snapshot HTML | [P] Pause | [K] Accélérer | [R] Reset Vitesse | [F11/F12] Save/Load")

    # --- 4. BOUCLE PRINCIPALE ---
    while not battle.finished and running:
        
        # A) Gestion des Inputs
        action = viewer.handle_input()

        if action == "quit":
            running = False

        elif action == "pause":
            is_paused = not is_paused
            state_str = "⏸ PAUSE" if is_paused else "▶ REPRISE"
            print(state_str)

        elif action == "accelerer":
            current_speed = 5
            print(f"⏩ VITESSE ACCÉLÉRÉE (x{current_speed})")

        elif action == "normal": # Touche R renvoyée par la vue
            current_speed = 1
            print("▶ VITESSE NORMALE (x1)")

        elif action == "switch_view":
            viewer.on_exit()
            viewer = IsometricView() if isinstance(viewer, TerminalView) else TerminalView()
            viewer.on_enter(battle, battle.get_state())

        elif action == "\t": 
            print("📸 Génération du snapshot HTML (Le combat continue...)")
            try:
                generate_snapshot_html(battle.players, battle.time)
            except Exception as e:
                print(f"⚠️ Erreur HUD : {e}")

        elif action == "save":
            battle.save_state()

        elif action == "load":
            loaded_battle = Battle.load_state()
            if loaded_battle:
                battle = loaded_battle 
                viewer.on_enter(battle, battle.get_state())
                print("📂 Partie chargée !")

        # B) Mise à jour de la Simulation
        if not is_paused:
            # Appel de la méthode update avec le paramètre speed (boucle interne de Battle)
            game_state = battle.update(speed=current_speed)
        else:
            # En pause, on récupère l'état statique pour l'affichage
            game_state = battle.get_state()

        # C) Rendu Visuel
        if game_state:
            viewer.render(game_state)
        # D) Limitation de la boucle d'affichage
        time.sleep(FRAME_DELAY)

    # --- 5. FIN DU COMBAT ET EXPORTS ---
    print_battle_summary(battle)

    if args.data:
        save_battle_report(args.data, battle, args)

    winner_name = battle.winner.name if battle.winner else "DRAW"
    survivors_data = []
    for p in battle.players:
        for u in p.squad:
            if u.current_hp > 0:
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

    for scenario_name in args.scenarios:
        # RÉCUPÉRATION DE LA CONFIG
        config = SCENARIO_CONFIG.get(scenario_name)
        if not config:
            print(f"⚠️ Scénario {scenario_name} ignoré (pas de config)")
            continue
            
        scenario_fn = config["fn"]
        extra_params = config.get("args", [])

        for ai1, ai2 in product(args.generals, repeat=2):
            for n in range(args.N):
                # Gestion de l'inversion
                if not args.na and n % 2 == 1:
                    a, b = ai2, ai1 
                else:
                    a, b = ai1, ai2

                general_a = get_general(a)
                general_b = get_general(b)

                # --- APPEL GÉNÉRALISÉ ---
                # On passe les paramètres du dictionnaire + les deux généraux
                players, world_map = scenario_fn(*extra_params, general_a, general_b)
                
                battle = Battle(players, world_map)
                battle_result = battle.run()

                # --- DÉTECTION DU VAINQUEUR ---
                actual_winner_ai_name = None
                if battle.winner == players[0]:
                    actual_winner_ai_name = a
                elif battle.winner == players[1]:
                    actual_winner_ai_name = b
                
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


def run_load(args):
    battle = Battle.load_state(args.savefile)
    if not battle:
        return

    viewer = TerminalView() if args.terminal else IsometricView()
    if viewer:
        viewer.on_enter(battle, battle.get_state())
    if isinstance(viewer, IsometricView):
        pygame.display.set_mode((1800, 1000))
    
    running = True
    print(f"🚀 Partie chargée : {battle.players[0].name} vs {battle.players[1].name}")
    print("👉 Appuyez sur [TAB] pour le HUD Tactique.")

    while not battle.finished and running:
        battle.update()
        game_state = battle.get_state()
        
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

        viewer.render(game_state)
        time.sleep(FRAME_DELAY)

    print_battle_summary(battle)



def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_battle(args)
    elif args.command == "plot":
        run_plot(args)
    elif args.command == "tourney":
        tourney(args)
    elif args.command == "load":
        run_load(args)

if __name__ == "cli_main":
    main()