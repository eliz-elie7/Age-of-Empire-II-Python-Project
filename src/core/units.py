# src/core/units.py

import math
import random
from enum import Enum
from typing import Optional, Tuple, List

TILE = 32.0  # 1 tile = 32 pixels

class UnitType(Enum):
    KNIGHT = "knight"
    PIKEMAN = "pikeman"
    CROSSBOWMAN = "crossbowman"
    LONGSWORDSMAN = "longswordsman"
    ELITESKIRMISHER = "eliteskirmisher"

class Unit:
    """Classe de base pour toutes les unités - RTS stable"""

    def __init__(self, x: float, y: float, player):
        self.x = x
        self.y = y
        self.player = player

        # Stats
        self.max_hp = self.get_max_hp()
        self.current_hp = self.max_hp
        self.is_alive = True

        # Ordres
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True

        # Combat
        self.attack_cooldown = 0.0
        self.attack_windup_timer = 0.0

        # Anti-deadlock
        self.idle_timer = 0.0

    # ===== MÉTHODES ABSTRAITES =====

    def get_max_hp(self) -> int: raise NotImplementedError
    def get_attack(self) -> int: raise NotImplementedError
    def get_melee_armor(self) -> int: raise NotImplementedError
    def get_pierce_armor(self) -> int: raise NotImplementedError
    def get_range(self) -> float: raise NotImplementedError
    def get_reload_time(self) -> float: raise NotImplementedError
    def get_speed(self) -> float: raise NotImplementedError
    def get_line_of_sight(self) -> float: raise NotImplementedError
    def get_symbol(self) -> str: raise NotImplementedError
    def get_collision_radius(self) -> float: raise NotImplementedError

    def can_occupy_same_space(self, other: 'Unit') -> bool:
        return False
    def get_damage_type(self) -> str:
        """Par défaut, tout le monde tape en mêlée sauf surcharge."""
        return "melee"

    def get_attack_windup(self) -> float:
        return 0.12

    # ===== DÉGÂTS =====

    def take_damage(self, damage: int, damage_type: str = "melee"):
        if not self.is_alive:
            return

        armor = 0
        if damage_type == "melee":
            armor = self.get_melee_armor()
        elif damage_type == "pierce":
            armor = self.get_pierce_armor()

        self.current_hp -= max(0, damage - armor)

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            self.clear_order()

    # ===== ORDRES =====

    def set_order(self, order_type: str, data: dict):
        self._current_order = order_type
        self._order_data = data
        self.needs_new_orders = False

    def clear_order(self):
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True

    def needs_order(self) -> bool:
        return self.needs_new_orders

    @property
    def current_order(self):
        return self._current_order
    def is_alive(self) -> bool:
        return self.current_hp > 0
    # ===== UPDATE PRINCIPALE =====

    def update(self, battle, delta_time: float):
        if not self.is_alive:
            return

        # cooldowns
        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)

        # windup attaque
        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0:
                target = self._order_data.get("target")
                if target and target.is_alive:
                    # --- CHANGEMENT IMPORTANT ICI ---
                    # 1. On calcule les dégâts complets (Base + Bonus)
                    dmg = self.get_total_damage(target)
                    # 2. On récupère le bon type (melee ou pierce)
                    dmg_type = self.get_damage_type()
                    # 3. On applique
                    target.take_damage(dmg, dmg_type)
                    # --------------------------------    
            return

        # anti idle
        self.idle_timer += delta_time
        if self._current_order is None and self.idle_timer > 1.5:
            self._jitter(battle)
            self.idle_timer = 0.0

        # exécution ordre
        if self._current_order == "move":
            self._execute_move_order(delta_time, battle)
        elif self._current_order == "attack":
            self._execute_attack_order(delta_time, battle)

    # ===== ORDRES =====

    def _execute_move_order(self, delta_time: float, battle):
        if "position" not in self._order_data:
            self.clear_order()
            return

        tx, ty = self._order_data["position"]
        self.move_toward(tx, ty, delta_time, battle)

        if self.has_reached_position(tx, ty):
            self.clear_order()

    def _execute_attack_order(self, delta_time: float, battle):
        target = self._order_data.get("target")
        if not target or not target.is_alive:
            self.clear_order()
            return

        dist = self.distance_to(target)

        if dist <= self.get_range():
            if self.attack_cooldown <= 0:
                self.attack_windup_timer = self.get_attack_windup()
                self.attack_cooldown = self.get_reload_time()
        else:
            self.move_toward(target.x, target.y, delta_time, battle)

    # ===== MOUVEMENT =====

    def move_toward(self, target_x: float, target_y: float, delta_time: float, battle):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.1:
            return

        move = min(self.get_speed() * delta_time, dist)
        nx = self.x + (dx / dist) * move
        ny = self.y + (dy / dist) * move

        world_map = getattr(battle, "world_map", None) or getattr(battle, "map", None)
        all_units = battle.all_units() if hasattr(battle, "all_units") else []

        if world_map and world_map.can_move_to(self, nx, ny, all_units):
            self.x, self.y = world_map.clamp_position(nx, ny)
        else:
            self._jitter(battle)

    def _jitter(self, battle):
        world_map = getattr(battle, "world_map", None)
        if not world_map:
            return

        angle = random.uniform(0, 2 * math.pi)
        r = self.get_collision_radius() * 0.5
        nx = self.x + math.cos(angle) * r
        ny = self.y + math.sin(angle) * r
        self.x, self.y = world_map.clamp_position(nx, ny)

    # ===== DISTANCES =====

    def distance_to(self, other: 'Unit') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def has_reached_position(self, x: float, y: float, margin: float = 5.0) -> bool:
        return (self.x - x)**2 + (self.y - y)**2 <= margin * margin

    #===== BONUS DE DÉGÂTS =====
    def get_bonus_damage(self, target: 'Unit') -> int:
        """Par défaut, aucun bonus"""
        return 0

    def get_damage_against(self, target: 'Unit') -> int:
        """Calcule les dégâts totaux avant armure"""
        return self.get_attack() + self.get_bonus_damage(target)
    def get_total_damage(self, target: 'Unit') -> int:
        
        """Calcul neutre : Attaque de base + Bonus éventuel."""
        return self.get_attack() + self.get_bonus_damage(target)
# ===== UNITÉS =====

class Knight(Unit):
    def get_max_hp(self): return 100
    def get_attack(self): return 10
    def get_melee_armor(self): return 2
    def get_pierce_armor(self): return 2
    def get_range(self): return 1.0 * TILE
    def get_reload_time(self): return 1.5
    def get_speed(self): return 1.35 * TILE
    def get_line_of_sight(self): return 6.0 * TILE
    def get_symbol(self): return "K"
    def get_collision_radius(self): return 0.5 * TILE
    def get_attack_windup(self): return 0.15
    def get_bonus_damage(self, target: 'Unit') -> int:
        # Bonus contre les arbalétriers (Crossbowman)
        if isinstance(target, Crossbowman):
            return 8  # Valeur AOE2
        return 0

class Pikeman(Unit):
    def get_max_hp(self): return 55
    def get_attack(self): return 4
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 1.0 * TILE
    def get_reload_time(self): return 3.0
    def get_speed(self): return 1.0 * TILE
    def get_line_of_sight(self): return 5.0 * TILE
    def get_symbol(self): return "P"
    def get_collision_radius(self): return 0.45 * TILE
    def get_attack_windup(self): return 0.20
    def get_bonus_damage(self, target: 'Unit') -> int:
        # Bonus massif contre la cavalerie (Knight)
        # On vérifie le type via isinstance ou le nom de classe
        if isinstance(target, Knight): 
            return 22  # Valeur AOE2
        # (Optionnel) Bonus contre War Elephant / Camel si tu les ajoutes
        return 0

class Crossbowman(Unit):
    def get_max_hp(self): return 35
    def get_attack(self): return 6
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 1
    def get_range(self): return 4.5 * TILE
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 8.0 * TILE
    def get_symbol(self): return "C"
    def get_collision_radius(self): return 0.45 * TILE
    def get_attack_windup(self): return 0.30
    def get_bonus_damage(self, target: 'Unit') -> int:
        # Petit bonus contre piquiers parfois, mais surtout dégâts de base
        # AOE2: Crossbowman a peu de bonus, c'est surtout le Skirmisher qui en a.
        return 0
    def get_damage_type(self) -> str:
        # RÈGLE OFFICIELLE : Les flèches sont des dégâts "pierce" (perçants)
        # Cela permet à l'armure "pierce_armor" des cibles de fonctionner.
        return "pierce"
    ##--unités supplémentaires ici--
    class LongSwordsman(Unit):
        """ Infanterie standard. Fort au corps à corps, bat les Piquiers et les Skirmishers, mais meurt contre les Chevaliers et Archers. """
        def get_max_hp(self): return 60
    def get_attack(self): return 9
    def get_melee_armor(self): return 1
    def get_pierce_armor(self): return 1
    def get_range(self): return 0.5 * TILE # Corps à corps strict
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.9 * TILE # Un peu lent
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "S" # S pour Swordsman
    def get_collision_radius(self): return 0.4 * TILE

    def get_bonus_damage(self, target: 'Unit') -> int:
        # Bonus standard vs Bâtiments (si tu en ajoutes plus tard) : +6
        # Bonus vs Aigles (pas dans le jeu pour l'instant)
        # Globalement, c'est une unité "stats pures", elle a peu de bonus spécifiques contre les unités.
        return 0
    
class EliteSkirmisher(Unit):
    """ Unité d'archer légère spécialisée dans le combat contre l'infanterie. """
    def get_max_hp(self): return 30
    def get_attack(self): return 5
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 5.0 * TILE
    def get_reload_time(self): return 1.5
    def get_speed(self): return 1.1 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "E" # E pour Elite Skirmisher
    def get_collision_radius(self): return 0.4 * TILE

    def get_bonus_damage(self, target: 'Unit') -> int:
        # Bonus significatif contre l'infanterie (LongSwordsman, Pikeman)
        if isinstance(target, (LongSwordsman, Pikeman)):
            return 7  # Bonus contre l'infanterie
        return 0
# ===== FACTORY =====

def create_unit(unit_type: UnitType, x: float, y: float, player) -> Unit:
    if unit_type == UnitType.KNIGHT:
        return Knight(x, y, player)
    if unit_type == UnitType.PIKEMAN:
        return Pikeman(x, y, player)
    if unit_type == UnitType.CROSSBOWMAN:
        return Crossbowman(x, y, player)
    # --- NOUVEAUX ---
    if unit_type == UnitType.LONGSWORDSMAN:
        return LongSwordsman(x, y, player)
    if unit_type == UnitType.ELITESKIRMISHER:
        return EliteSkirmisher(x, y, player)
        
    raise ValueError(f"Type d'unité inconnu: {unit_type}")


# import math
# from enum import Enum
# from typing import Optional, Tuple, List

# class UnitType(Enum):
#     KNIGHT = "knight"
#     PIKEMAN = "pikeman"
#     CROSSBOWMAN = "crossbowman"

# class Player(Enum):
#     PLAYER1 = 1
#     PLAYER2 = 2

# class Unit:
#     """Classe de base pour toutes les unités"""
    
#     def __init__(self, x: int, y: int, player: Player):
#         self.x = x
#         self.y = y
#         self.player = player
#         self.max_hp = self.get_max_hp()
#         self.current_hp = self.max_hp
#         self.last_attack_time = 0
#         self.target: Optional['Unit'] = None
#         self.is_alive = True
    
#     def get_max_hp(self) -> int:
#         """HP maximal selon le type d'unité"""
#         raise NotImplementedError
    
#     def get_attack(self) -> int:
#         """Dégâts de base"""
#         raise NotImplementedError
    
#     def get_melee_armor(self) -> int:
#         """Armure mêlée"""
#         raise NotImplementedError
    
#     def get_pierce_armor(self) -> int:
#         """Armure à distance"""
#         raise NotImplementedError
    
#     def get_range(self) -> int:
#         """Portée d'attaque"""
#         raise NotImplementedError
    
#     def get_reload_time(self) -> float:
#         """Temps de rechargement entre attaques (en secondes)"""
#         raise NotImplementedError
    
#     def get_speed(self) -> float:
#         """Vitesse de déplacement en pixels/seconde"""
#         raise NotImplementedError
    
#     def get_collision_radius(self) -> float:
#         """Retourne le rayon de collision en pixels"""
#         raise NotImplementedError
    
#     def get_line_of_sight(self) -> int:
#         """Ligne de vue"""
#         raise NotImplementedError
    
#     def get_symbol(self) -> str:
#         """Symbole pour affichage terminal"""
#         raise NotImplementedError
    
#     def get_bonus_damage(self, target: 'Unit') -> int:
#         """Dégâts bonus contre certains types d'unités"""
#         return 0
    
#     def distance_to(self, other: 'Unit') -> float:
#         """Distance euclidienne vers une autre unité"""
#         return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
#     def can_attack(self, target: 'Unit', current_time: float) -> bool:
#         """Vérifie si l'unité peut attaquer la cible"""
#         if not target.is_alive:
#             return False
#         if target.player == self.player:
#             return False
#         if self.distance_to(target) > self.get_range():
#             return False
#         if current_time - self.last_attack_time < self.get_reload_time():
#             return False
#         return True
    
#     def attack(self, target: 'Unit', current_time: float, battlefield=None) -> int:
#         """Attaque une cible et retourne les dégâts infligés"""
#         if not self.can_attack(target, current_time):
#             return 0
        
#         base_damage = self.get_attack()
#         bonus_damage = self.get_bonus_damage(target)
#         total_attack = base_damage + bonus_damage
        
#         # Appliquer l'armure appropriée
#         if self.get_range() > 0:  # Attaque à distance
#             armor = target.get_pierce_armor()
#         else:  # Attaque mêlée
#             armor = target.get_melee_armor()
        
#         # Formule AOE2: max(1, attack - armor)
#         final_damage = max(1, total_attack - armor)
        
#         target.take_damage(final_damage, battlefield)
#         self.last_attack_time = current_time
        
#         return final_damage
    
#     def take_damage(self, damage: int, battlefield=None):
#         """Prend des dégâts"""
#         self.current_hp -= damage
#         if self.current_hp <= 0:
#             self.current_hp = 0
#             if self.is_alive:  # Si c'était vivant et maintenant mort
#                 if battlefield:
#                     battlefield.register_death(self.x, self.y)
#             self.is_alive = False
    
#     def move_towards(self, target_x: int, target_y: int):
#         """Se déplace vers une position (simple, 1 case à la fois)"""
#         if self.x < target_x:
#             self.x += 1
#         elif self.x > target_x:
#             self.x -= 1
        
#         if self.y < target_y:
#             self.y += 1
#         elif self.y > target_y:
#             self.y -= 1
    
#     def order_data(self) -> dict:
#         """Retourne les données de l'unité pour l'ordre"""
#         return {
#             'type': self.__class__.__name__,
#             'x': self.x,
#             'y': self.y,
#             'player': self.player.name,
#             'current_hp': self.current_hp,
#             'is_alive': self.is_alive
#         }
        
#     def needs_new_order(self) -> bool:
#         """Détermine si l'unité a besoin d'un nouvel ordre"""
#         return self.target is None or not self.target.is_alive


# class Pikeman(Unit):
#     """Piquier - Infanterie anti-cavalerie"""
    
#     def get_max_hp(self) -> int:
#         return 55
    
#     def get_attack(self) -> int:
#         return 4
    
#     def get_melee_armor(self) -> int:
#         return 0
    
#     def get_pierce_armor(self) -> int:
#         return 0
    
#     def get_range(self) -> int:
#         return 1  # Mêlée
    
#     def get_reload_time(self) -> float:
#         return 3.0
    
#     def get_speed(self) -> float:
#         return 80.0
    
#     def get_line_of_sight(self) -> int:
#         return 4
    
#     def get_symbol(self) -> str:
#         """Symbole pour affichage terminal"""
#         return 'P'
    
#     def get_collision_radius(self):
#         return 5.0
    
#     def get_bonus_damage(self, target: Unit) -> int:
#         """Bonus massif contre cavalerie"""
#         if isinstance(target, Knight):
#             return 22 # Bonus anti-cavalerie
#         return 0



# def create_unit(unit_type: UnitType, x: int, y: int, player: Player) -> Unit:
#     """Factory pour créer une unité"""
#     if unit_type == UnitType.PIKEMAN:
#         return Pikeman(x, y, player)
#     else:
#         raise ValueError(f"Type d'unité inconnu: {unit_type}")