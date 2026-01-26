# test_units.py
from src.core import create_unit, UnitType, Player, Map
import time

def test_unit_movement():
    print("🎯 TEST DU MOUVEMENT DES UNITÉS")
    
    player = Player("Test", None)
    unit = create_unit(UnitType.KNIGHT, 100, 150, player)
    world_map = Map(600, 300)  # ✅ Créer une map pour le test
    
    print(f"Initial position: ({unit.x}, {unit.y})")
    print(f"Unit speed: {unit.get_speed()}")
    print(f"Unit needs orders: {unit.needs_new_orders}")
    
    # Donner un ordre manuel
    unit.set_order('move', {'position': (300, 150)})
    print(f"After set_order - needs orders: {unit.needs_new_orders}")
    print(f"Current order: {unit.current_order}")
    print(f"Order data: {unit.order_data}")
    
    # Créer un objet mock pour battle
    class MockBattle:
        def __init__(self, world_map):
            self.world_map = world_map
        def all_units(self):
            return []  # Pas d'autres unités pour les collisions
    
    mock_battle = MockBattle(world_map)
    
    # Simuler quelques updates
    for i in range(10):  # Plus d'updates pour voir le mouvement
        print(f"\n--- Update {i+1} ---")
        unit.update(mock_battle, 0.1)  # ✅ Utiliser mock_battle avec map
        print(f"Position: ({unit.x:.1f}, {unit.y:.1f})")
        print(f"Needs orders: {unit.needs_new_orders}")
        
        if unit.needs_new_orders:
            print("✅ Unit finished movement!")
            break
        elif i == 9:
            print("⚠️  Unit still moving after 10 updates")
    
    moved = unit.x > 100 + 1.0  # Vérifier que l'unité a bougé d'au moins 1 pixel
    print(f"\nFinal position: ({unit.x:.1f}, {unit.y:.1f})")
    print(f"✅ Test mouvement {'réussi' if moved else 'échoué'} - Movement: {unit.x - 100:.1f} pixels")
    
    return moved

if __name__ == "__main__":
    test_unit_movement()