# main_debug.py
from src.core import Battle, Map, Player, create_unit, UnitType
from src.ai import BrainDead, Daft
from src.vis.terminal_view import TerminalView
import time
import random

def main_debug():
    print("🐛 MAIN DEBUG - DÉMARRAGE")
    
    # 1. Création des généraux
    print("🤖 Création des généraux...")
    general_a = BrainDead()
    general_b = Daft()
    
    # 2. Création des joueurs
    print("👥 Création des joueurs...")
    player_a = Player("Player A", general_a)
    player_b = Player("Player B", general_b)
    
    # 3. Ajout des unités avec positions éloignées
    print("⚔️ Création des unités...")
    for i in range(3):
        # Player A - côté gauche
        knight_a = create_unit(UnitType.KNIGHT, 100 + i*80, 150, player_a)
        player_a.add_unit(knight_a)
        print(f"   👉 {player_a.name}: {knight_a.get_symbol()} at ({knight_a.x}, {knight_a.y})")
        
        # Player B - côté droit  
        knight_b = create_unit(UnitType.KNIGHT, 400 + i*80, 150, player_b)
        player_b.add_unit(knight_b)
        print(f"   👉 {player_b.name}: {knight_b.get_symbol()} at ({knight_b.x}, {knight_b.y})")
    
    # 4. Création de la carte et bataille
    print("🗺️ Création de la carte...")
    world_map = Map(600, 300)
    battle = Battle(
        players=[player_a, player_b],
        world_map=world_map,
        logic_dt=0.1,    # Plus lent pour debug
        max_time=30.0    # 30 secondes max
    )
    
    # 5. VISUALISATION SIMPLIFIÉE
    print("👀 Initialisation visualisation...")
    
    # 6. ✅ FORCER TOUTES LES UNITÉS À DEMANDER DES ORDRES
    print("\n🎯 RÉINITIALISATION DES ORDRES...")
    for player in battle.players:
        for unit in player.alive_units():
            unit.needs_new_orders = True  # ⚠️ FORCER la demande
            print(f"   🆕 {unit.get_symbol()} -> needs_new_orders = {unit.needs_new_orders}")
    
    # 7. BOUCLE PRINCIPALE AVEC LOGGING DÉTAILLÉ
    print("\n🚀 DÉMARRAGE DE LA BOUCLE PRINCIPALE...")
    print("=" * 60)
    
    start_time = time.time()
    frame_count = 0
    last_log_time = start_time
    
    while not battle.finished and battle.game_time < battle.max_time:
        frame_count += 1
        current_time = time.time()
        
        # Mettre à jour le temps de jeu
        battle.game_time = current_time - start_time
        
        print(f"\n🎮 FRAME {frame_count} | Temps: {battle.game_time:.1f}s")
        print("-" * 40)
        
        # A. ÉTAT AVANT UPDATE
        print("📊 ÉTAT AVANT UPDATE:")
        for i, player in enumerate(battle.players):
            moving_units = 0
            needing_orders = 0
            
            for unit in player.alive_units():
                if unit.current_order == 'move':
                    moving_units += 1
                if unit.needs_new_orders:
                    needing_orders += 1
            
            print(f"   {player.name}: {len(player.alive_units())} units | "
                  f"{moving_units} moving | {needing_orders} needing orders")
        
        # B. UPDATE BATTLE
        game_state = battle.update()
        
        # C. ÉTAT APRÈS UPDATE  
        print("📊 ÉTAT APRÈS UPDATE:")
        for i, player in enumerate(battle.players):
            moving_units = 0
            for unit in player.alive_units():
                if unit.current_order == 'move':
                    moving_units += 1
                    target_pos = unit.order_data.get('position', '?')
                    print(f"   🚀 {unit.get_symbol()} moving to {target_pos} "
                          f"at ({unit.x:.1f}, {unit.y:.1f})")
            
            if moving_units == 0:
                print(f"   💤 {player.name}: aucune unité en mouvement")
        
        # D. AFFICHAGE VISUEL (optionnel)
        try:
            viewer = TerminalView(fps=10)
            viewer.display(game_state)
        except Exception as e:
            print(f"   👁️  Visualisation skipped: {e}")
        
        # E. PAUSE POUR LIRE LES LOGS
        time_since_last_log = current_time - last_log_time
        if time_since_last_log < 1.0:  # Attendre 1s entre les frames en debug
            time.sleep(1.0 - time_since_last_log)
        last_log_time = current_time
        
        # F. CHECK TIMEOUT
        if frame_count > 50:  # Sécurité anti-boucle infinie
            print("⏰ TIMEOUT - Arrêt après 50 frames")
            break
    
    # 8. RÉSULTAT FINAL
    print("\n" + "=" * 60)
    print("🏁 RÉSULTAT FINAL")
    
    final_state = battle.get_game_state()
    if final_state['winner']:
        print(f"🎉 VICTOIRE: {final_state['winner']}")
    else:
        print("🤝 MATCH NUL ou TIMEOUT")
    
    print(f"⏱️  Durée: {battle.game_time:.1f}s")
    print(f"🎮 Frames: {frame_count}")
    
    # Détail final des unités
    for player in battle.players:
        alive_count = len(player.alive_units())
        print(f"   {player.name}: {alive_count} unités survivantes")
        for unit in player.alive_units():
            print(f"     {unit.get_symbol()} at ({unit.x:.1f}, {unit.y:.1f}) - "
                  f"HP: {unit.current_hp} - Order: {unit.current_order}")

def test_initial_orders():
    """Test rapide pour vérifier que les généraux fonctionnent au début"""
    print("\n🔍 TEST INITIAL DES ORDRES")
    
    general = Daft()
    player = Player("Test", general)
    enemy = Player("Enemy", BrainDead())
    
    # Créer des unités
    knight = create_unit(UnitType.KNIGHT, 100, 150, player)
    enemy_knight = create_unit(UnitType.KNIGHT, 400, 150, enemy)
    
    player.add_unit(knight)
    enemy.add_unit(enemy_knight)
    
    map_obj = Map(600, 300)
    
    # Tester give_orders
    units_needing = [knight]
    orders = general.give_orders(player, [player, enemy], map_obj, units_needing)
    
    print(f"📨 Orders générés: {len(orders)}")
    for order in orders:
        print(f"   - {order['type']} for {order['unit'].get_symbol()}")
        
        # Appliquer l'ordre
        order['unit'].set_order(order['type'], 
                              {k: v for k, v in order.items() if k not in ['type', 'unit']})
        
        if order['type'] == 'move':
            target = order.get('position', '?')
            print(f"     🎯 Target: {target}")
        elif order['type'] == 'attack':
            target = order.get('target', '?')
            print(f"     🎯 Target: {target.get_symbol() if hasattr(target, 'get_symbol') else '?'}")

if __name__ == "__main__":
    print("🎯 DÉMARRAGE DU DEBUG COMPLET")
    print("=" * 60)
    
    # Lancer le test initial d'abord
    test_initial_orders()
    
    print("\n" + "=" * 60)
    print("🎮 LANCEMENT DE LA SIMULATION COMPLÈTE")
    print("=" * 60)
    
    # Lancer la simulation principale
    main_debug()