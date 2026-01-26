# test_generals.py
from src.ai import BrainDead, Daft
from src.core import Player, create_unit, UnitType, Map

def test_generals():
    print("🎯 TEST DES GÉNÉRAUX")
    
    general = Daft()  # Test avec Daft d'abord
    player = Player("Test", general)
    
    # Créer quelques unités
    knight = create_unit(UnitType.KNIGHT, 100, 150, player)
    player.add_unit(knight)
    
    # Créer un ennemi
    enemy_player = Player("Enemy", BrainDead())
    enemy_knight = create_unit(UnitType.KNIGHT, 300, 150, enemy_player)
    enemy_player.add_unit(enemy_knight)
    
    map_obj = Map(600, 300)
    
    # Tester give_orders
    units_needing = [knight]
    orders = general.give_orders(player, [player, enemy_player], map_obj, units_needing)
    
    print(f"📨 Orders générés: {len(orders)}")
    for order in orders:
        print(f"  - Type: {order['type']}, Unit: {order['unit'].get_symbol()}")
    
    return len(orders) > 0

if __name__ == "__main__":
    success = test_generals()
    print(f"✅ Test {'réussi' if success else 'échoué'}")