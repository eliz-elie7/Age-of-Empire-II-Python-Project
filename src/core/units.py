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
    def __init__(self, x: float, y: float, player):
        self.x = x
        self.y = y
        self.player = player
        self.max_hp = self.get_max_hp()
        self.current_hp = self.max_hp
        self.is_alive = True
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True
        self.attack_cooldown = 0.0
        self.attack_windup_timer = 0.0
        self.direction = "down"
        self.battle = None

    # ===== MÉTHODES ABSTRAITES (Stats) =====
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

    # ===== LOGIQUE DE COMBAT (Fusionnée) =====
    def get_bonus_damage(self, target: 'Unit') -> int:
        return 0  # Surchargé dans les sous-classes

    def get_damage_type(self) -> str:
        return "melee"  # Surchargé pour les archers

    def take_damage(self, damage: int, damage_type: str = "melee"):
        if not self.is_alive: return
        armor = self.get_melee_armor() if damage_type == "melee" else self.get_pierce_armor()
        self.current_hp -= max(1, damage - armor) # Minimum 1 dégât
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            self.clear_order()

    def _apply_combat_damage(self):
        target = self._order_data.get("target")
        if target and target.is_alive:
            # Calcul base + bonus (Diallo)
            raw_dmg = self.get_attack() + self.get_bonus_damage(target)
            
            # Modificateur de hauteur (Chef)
            my_el = self.battle.world_map.get_elevation_at(self.x, self.y)
            target_el = self.battle.world_map.get_elevation_at(target.x, target.y)
            
            if my_el > target_el: raw_dmg *= 1.25
            elif my_el < target_el: raw_dmg *= 0.75
            
            target.take_damage(int(raw_dmg), self.get_damage_type())
            self.attack_cooldown = self.get_reload_time()
            if not target.is_alive: self.clear_order()

    # ===== MOUVEMENT (Ta version stable) =====
    def _compute_steering(self, battle) -> Tuple[float, float]:
        vx, vy = 0.0, 0.0
        target_pos = None

        if self._current_order == "move":
            target_pos = self._order_data.get("position")
        elif self._current_order == "attack":
            target = self._order_data.get("target")
            if target and target.is_alive:
                dist = self.distance_to(target)
                # On utilise la portée réelle sans "visual overlap" pour éviter le bégaiement
                eff_range = self.get_range() + self.get_collision_radius() + target.get_collision_radius()
                if dist > eff_range:
                    target_pos = (target.x, target.y)

        if target_pos:
            dx, dy = target_pos[0] - self.x, target_pos[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0.1:
                # Modificateur de vitesse par élévation
                c_el = battle.world_map.get_elevation_at(self.x, self.y)
                t_el = battle.world_map.get_elevation_at(target_pos[0], target_pos[1])
                speed_mod = 0.6 if t_el > c_el else (1.2 if t_el < c_el else 1.0)
                vx = (dx / dist) * self.get_speed() * speed_mod
                vy = (dy / dist) * self.get_speed() * speed_mod

        # Séparation (Anti-empilement)
        for other in battle.all_units():
            if other is self or not other.is_alive: continue
            dx, dy = self.x - other.x, self.y - other.y
            dist_sq = dx*dx + dy*dy
            min_dist = (self.get_collision_radius() + other.get_collision_radius()) * 0.9
            if dist_sq < min_dist * min_dist and dist_sq > 0:
                d = math.sqrt(dist_sq)
                push = (min_dist - d) / min_dist
                vx += (dx / d) * push * self.get_speed() * 1.5
                vy += (dy / d) * push * self.get_speed() * 1.5
        return vx, vy

    def update(self, battle, delta_time: float):
        if not self.is_alive: return
        self.battle = battle
        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)

        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0: self._apply_combat_damage()
            return

        if self._current_order == "attack":
            target = self._order_data.get("target")
            if not target or not target.is_alive:
                self.clear_order()
                return
            self._update_direction(target.x - self.x, target.y - self.y)
            
            dist = self.distance_to(target)
            eff_range = self.get_range() + self.get_collision_radius() + target.get_collision_radius()
            
            if dist <= eff_range + 5.0: # Marge de tolérance
                if self.attack_cooldown <= 0:
                    self.attack_windup_timer = 0.12 # Windup court
                return

        vx, vy = self._compute_steering(battle)
        if vx != 0 or vy != 0:
            if self._current_order != "attack": self._update_direction(vx, vy)
            nx, ny = self.x + vx * delta_time, self.y + vy * delta_time
            # Glissade
            if battle.world_map.can_move_to(self, nx, ny, battle.all_units()):
                self.x, self.y = nx, ny
            elif battle.world_map.can_move_to(self, nx, self.y, battle.all_units()):
                self.x = nx
            elif battle.world_map.can_move_to(self, self.x, ny, battle.all_units()):
                self.y = ny
            self.x, self.y = battle.world_map.clamp_position(self.x, self.y)

    def _update_direction(self, dx: float, dy: float):
        if abs(dx) < 0.01 and abs(dy) < 0.01: return
        angle = math.degrees(math.atan2(dy, dx))
        if -45 <= angle <= 45: self.direction = "right"
        elif 45 < angle <= 135: self.direction = "down"
        elif -135 <= angle < -45: self.direction = "up"
        else: self.direction = "left"

    def set_order(self, order_type: str, data: dict):
        self._current_order = order_type
        self._order_data = data
        self.needs_new_orders = False

    def clear_order(self):
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True

    def distance_to(self, other: 'Unit') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

# ===== UNITÉS SPÉCIFIQUES =====

class Knight(Unit):
    def get_max_hp(self): return 100
    def get_attack(self): return 10
    def get_melee_armor(self): return 2
    def get_pierce_armor(self): return 2
    def get_range(self): return 2.0 # Mêlée quasi-contact
    def get_reload_time(self): return 1.8
    def get_speed(self): return 1.35 * TILE
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "K"
    def get_collision_radius(self): return 0.20 * TILE

class Pikeman(Unit):
    def get_max_hp(self): return 55
    def get_attack(self): return 4
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 3.0
    def get_reload_time(self): return 3.0
    def get_speed(self): return 1.0 * TILE
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "P"
    def get_collision_radius(self): return 0.15 * TILE
    def get_bonus_damage(self, target):
        return 22 if isinstance(target, Knight) else 0

class Crossbowman(Unit):
    def get_max_hp(self): return 35
    def get_attack(self): return 5
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 5.0 * TILE
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "C"
    def get_collision_radius(self): return 0.15 * TILE
    def get_damage_type(self): return "pierce"

class LongSwordsman(Unit):
    def get_max_hp(self): return 60
    def get_attack(self): return 9
    def get_melee_armor(self): return 1
    def get_pierce_armor(self): return 1
    def get_range(self): return 2.0
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.9 * TILE
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "S"
    def get_collision_radius(self): return 0.15 * TILE

class EliteSkirmisher(Unit):
    def get_max_hp(self): return 30
    def get_attack(self): return 3
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 4
    def get_range(self): return 5.0 * TILE
    def get_reload_time(self): return 3.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "E"
    def get_collision_radius(self): return 0.15 * TILE
    def get_damage_type(self): return "pierce"
    def get_bonus_damage(self, target):
        if isinstance(target, (Crossbowman, Pikeman)): return 4
        return 0

def create_unit(unit_type: UnitType, x: float, y: float, player) -> Unit:
    mapping = {
        UnitType.KNIGHT: Knight,
        UnitType.PIKEMAN: Pikeman,
        UnitType.CROSSBOWMAN: Crossbowman,
        UnitType.LONGSWORDSMAN: LongSwordsman,
        UnitType.ELITESKIRMISHER: EliteSkirmisher
    }
    if unit_type in mapping: return mapping[unit_type](x, y, player)
    raise ValueError(f"Type inconnu: {unit_type}")