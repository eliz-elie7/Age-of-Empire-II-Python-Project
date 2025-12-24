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
                    target.take_damage(self.get_attack(), "melee")
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

# ===== FACTORY =====

def create_unit(unit_type: UnitType, x: float, y: float, player) -> Unit:
    if unit_type == UnitType.KNIGHT:
        return Knight(x, y, player)
    if unit_type == UnitType.PIKEMAN:
        return Pikeman(x, y, player)
    if unit_type == UnitType.CROSSBOWMAN:
        return Crossbowman(x, y, player)
    raise ValueError(f"Type d'unité inconnu: {unit_type}")
