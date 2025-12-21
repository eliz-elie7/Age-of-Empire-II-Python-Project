from .General import General

class Daft(General):
    def __init__(self):
        super().__init__("Daft")

    def give_orders(self, current_player, all_players, map, units_needing_orders):
        orders = []
        
        for unit in units_needing_orders:
            # Cherche d'abord les ennemis en vue
            enemies_in_sight = self.get_enemies_in_sight(unit, all_players)
            
            if enemies_in_sight:
                closest_enemy = self.get_closest_enemy(unit, enemies_in_sight)
                # DONNER DIRECTEMENT UN ORDRE 'attack' : l'unité se déplacera si nécessaire
                order = {'type': 'attack', 'unit': unit, 'target': closest_enemy}
            else:
                # Cherche l'ennemi le plus proche sur toute la carte
                all_enemies = self.get_all_enemies(unit, all_players)
                closest_enemy = self.get_closest_enemy(unit, all_enemies)
                if closest_enemy:
                    # attaquer une cible lointaine (l'unité avancera)
                    order = {'type': 'attack', 'unit': unit, 'target': closest_enemy}
                else:
                    order = {'type': 'hold', 'unit': unit}
            
            if order:
                orders.append(order)
        
        return orders

    def get_enemies_in_sight(self, unit, all_players):
        """Ennemis dans la ligne de vue"""
        enemies = []
        sight_range = unit.get_line_of_sight()
        
        for player in all_players:
            if player != unit.player:
                for enemy_unit in player.get_alive_units():
                    if unit.distance_to(enemy_unit) <= sight_range:
                        enemies.append(enemy_unit)
        return enemies

    def get_all_enemies(self, unit, all_players):
        """Tous les ennemis vivants"""
        enemies = []
        for player in all_players:
            if player != unit.player:
                enemies.extend(player.get_alive_units())
        return enemies

    def get_closest_enemy(self, unit, enemies):
        """Trouve l'ennemi le plus proche dans une liste"""
        if not enemies:
            return None
        
        closest_enemy = enemies[0]
        min_distance = unit.distance_to(closest_enemy)
        
        for enemy in enemies[1:]:
            distance = unit.distance_to(enemy)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        
        return closest_enemy

    def _decide_combat_action(self, unit, enemy, map):
        """Maintenu pour compatibilité, mais désormais on attaque toujours via give_orders"""
        if enemy is None:
            return {'type': 'hold', 'unit': unit}
        return {'type': 'attack', 'unit': unit, 'target': enemy}

    def _decide_movement_action(self, unit, enemy, map):
        """Maintenu pour compatibilité"""
        if enemy is None:
            return {'type': 'hold', 'unit': unit}
        return {'type': 'move', 'unit': unit, 'position': (enemy.x, enemy.y)}

    def _calculate_movement_order(self, unit, enemy, map):
        """Conserve un fallback mais n'est plus central pour Daft"""
        if enemy is None:
            return {'type': 'hold', 'unit': unit}

        dx = enemy.x - unit.x
        dy = enemy.y - unit.y
        distance = unit.distance_to(enemy)
        
        if distance == 0:
            return {'type': 'hold', 'unit': unit}
        
        approach_distance = max(0.0, distance - unit.get_range())
        # Utiliser un facteur de pas proportionnel à la vitesse pour avancer plus naturellement
        move_distance = unit.get_speed() * 0.05  # petit pas stable
        move_factor = (move_distance / distance) if distance > 0 else 0.0
        move_factor = min(1.0, move_factor)

        target_x = unit.x + dx * move_factor
        target_y = unit.y + dy * move_factor
        
        return {'type': 'move', 'unit': unit, 'position': (target_x, target_y)}
