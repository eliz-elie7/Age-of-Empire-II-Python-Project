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

        self.direction = "down"  # Pour l'affichage, valeurs : up, down, left, right

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

    """def _apply_soft_separation(self, battle, delta_time: float):
        #Remplace le jitter brutal par une répulsion douce entre unités.
        all_units = battle.all_units()
        push_force_x = 0
        push_force_y = 0
        
        for other in all_units:
            if other is self:
                continue
            
            dx = self.x - other.x
            dy = self.y - other.y
            dist_sq = dx*dx + dy*dy
            
            # Rayon de collision combiné
            min_dist = (self.get_collision_radius() + other.get_collision_radius()) * 0.8
            
            if dist_sq < min_dist * min_dist and dist_sq > 0:
                dist = math.sqrt(dist_sq)
                # Force de répulsion : plus on est proche, plus on pousse
                overlap = min_dist - dist
                push_force_x += (dx / dist) * overlap
                push_force_y += (dy / dist) * overlap

        # Appliquer la poussée progressivement (on lisse avec delta_time)
        if push_force_x != 0 or push_force_y != 0:
            speed_factor = 2.0 # Ajuste pour plus ou moins de nervosité
            nx = self.x + push_force_x * delta_time * speed_factor
            ny = self.y + push_force_y * delta_time * speed_factor
            
            # On vérifie juste les limites de la map
            self.x, self.y = battle.world_map.clamp_position(nx, ny)

    def update(self, battle, delta_time: float):
        if not self.is_alive:
            return

        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)

        # 1. Si on attaque (windup), on est "ancré" au sol, pas de mouvement
        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0:
                target = self._order_data.get("target")
                if target and target.is_alive:
                    dmg = max(1, self.get_attack() - target.get_melee_armor())
                    target.take_damage(dmg, "melee")
            return

        # 2. Séparation douce (remplace le jitter)
        # On l'applique presque tout le temps pour que les unités ne s'empilent jamais
        self._apply_soft_separation(battle, delta_time)

        # 3. Exécution des ordres
        if self._current_order == "move":
            self._execute_move_order(delta_time, battle)
        elif self._current_order == "attack":
            self._execute_attack_order(delta_time, battle)"""

    def _apply_combat_damage(self):
        target = self._order_data.get("target")
        if target and target.is_alive:
            # Calcul des dégâts de base
            base_dmg = max(1, self.get_attack() - target.get_melee_armor())
            
            # --- LOGIQUE DE HAUTEUR ---
            # 'battle' doit être accessible ou passé en argument, 
            # sinon on utilise self.battle si tu l'as stocké à l'init
            my_el = self.battle.world_map.get_elevation_at(self.x, self.y)
            target_el = self.battle.world_map.get_elevation_at(target.x, target.y)
            
            final_dmg = base_dmg
            if my_el > target_el:
                final_dmg = int(base_dmg * 1.3) # +30% de bonus
            elif my_el < target_el:
                final_dmg = int(base_dmg * 0.8) # -20% de malus

            dtype = "pierce" if self.get_symbol() == "C" else "melee"
            target.take_damage(final_dmg, dtype)
            
            self.attack_cooldown = self.get_reload_time()
            
            if not target.is_alive:
                self.clear_order()

    def _compute_steering(self, battle) -> Tuple[float, float]:
        vx, vy = 0.0, 0.0
        target_pos = None

        # --- A. DIRECTION ---
        if self._current_order == "move":
            target_pos = self._order_data.get("position")
        elif self._current_order == "attack":
            target = self._order_data.get("target")
            if target and target.is_alive:
                dist = self.distance_to(target)
                eff_range = (self.get_range() + self.get_collision_radius() + target.get_collision_radius()) - 2.0
                if dist > eff_range:
                    target_pos = (target.x, target.y)

        if target_pos:
            dx = target_pos[0] - self.x
            dy = target_pos[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0.1:
                # --- LOGIQUE D'ÉLÉVATION ---
                current_el = battle.world_map.get_elevation_at(self.x, self.y)
                target_el = battle.world_map.get_elevation_at(target_pos[0], target_pos[1])
                
                speed_mod = 1.0
                if target_el > current_el:
                    speed_mod = 0.6  # Ralentissement en montée (-40%)
                elif target_el < current_el:
                    speed_mod = 1.2  # Bonus en descente (+20%)

                vx = (dx / dist) * self.get_speed() * speed_mod
                vy = (dy / dist) * self.get_speed() * speed_mod

        # --- B. SÉPARATION (Inchangée mais essentielle) ---
        all_units = battle.all_units()
        sep_x, sep_y = 0.0, 0.0
        for other in all_units:
            if other is self or not other.is_alive: continue
            dx, dy = self.x - other.x, self.y - other.y
            dist_sq = dx*dx + dy*dy
            min_dist = (self.get_collision_radius() + other.get_collision_radius()) * 0.9
            
            if dist_sq < min_dist * min_dist and dist_sq > 0:
                d = math.sqrt(dist_sq)
                push = (min_dist - d) / min_dist
                sep_x += (dx / d) * push * self.get_speed() * 1.5
                sep_y += (dy / d) * push * self.get_speed() * 1.5

        return vx + sep_x, vy + sep_y

    def update(self, battle, delta_time: float):
        if not self.is_alive: return
        
        # On garde une référence pour les calculs internes
        self.battle = battle 

        # 1. Gestion des Cooldowns
        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)

        # 2. Gestion du Windup (Animation d'attaque en cours)
        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0:
                self._apply_combat_damage()
            return

        # 3. Logique de Cible et Orientation de Combat
        if self._current_order == "attack":
            target = self._order_data.get("target")
            if not target or not target.is_alive:
                self.clear_order()
                return

            # --- FACE-À-FACE : On s'oriente vers l'ennemi ---
            dx_face = target.x - self.x
            dy_face = target.y - self.y
            self._update_direction(dx_face, dy_face)

            dist = self.distance_to(target)
            
            # Bonus de portée si on domine l'adversaire
            my_el = battle.world_map.get_elevation_at(self.x, self.y)
            target_el = battle.world_map.get_elevation_at(target.x, target.y)
            range_bonus = 15.0 if my_el > target_el else 0.0
            
            eff_range = (self.get_range() + range_bonus + self.get_collision_radius() + target.get_collision_radius()) + 5.0
            
            if dist <= eff_range:
                if self.attack_cooldown <= 0:
                    self.attack_windup_timer = self.get_attack_windup()
                    return 
                else:
                    return # En attente du cooldown, l'unité reste face à l'ennemi

        # 4. Mouvement et Glissade
        vx, vy = self._compute_steering(battle)

        if vx != 0 or vy != 0:
            # Si on bouge et qu'on n'est pas en combat, on s'oriente vers le mouvement
            if self._current_order != "attack":
                self._update_direction(vx, vy)

            nx = self.x + vx * delta_time
            ny = self.y + vy * delta_time
            
            all_units = battle.all_units()
            
            # --- LOGIQUE DE GLISSADE CONTRE LE RELIEF ---
            if battle.world_map.can_move_to(self, nx, ny, all_units):
                self.x, self.y = nx, ny
            else:
                # On tente de glisser sur l'axe X
                if battle.world_map.can_move_to(self, nx, self.y, all_units):
                    self.x = nx
                # Ou sur l'axe Y
                elif battle.world_map.can_move_to(self, self.x, ny, all_units):
                    self.y = ny
            
            # Enfin, on reste dans les limites
            self.x, self.y = battle.world_map.clamp_position(self.x, self.y)

    def _update_direction(self, dx: float, dy: float):
        """Calcule et stocke la direction cardinale (indépendant de la vue)"""
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            return # On garde la direction précédente si pas de vecteur
            
        angle = math.degrees(math.atan2(dy, dx))
        # Logique isométrique : 4 directions
        if -45 <= angle <= 45: 
            self.direction = "right"
        elif 45 < angle <= 135: 
            self.direction = "down"
        elif -135 <= angle < -45: 
            self.direction = "up"
        else: 
            self.direction = "left"
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
        
        # FORMULE : Portée de la stat + Rayon de l'attaquant + Rayon de la cible
        # On ajoute 2 pixels de marge pour la précision des flottants
        visual_overlap = 15.0 # pour gerer le chevauchement visuel
        effective_range = (self.get_range() + 
                  self.get_collision_radius() + 
                  target.get_collision_radius()) - visual_overlap

        if dist <= effective_range:
            if self.attack_cooldown <= 0:
                self.attack_windup_timer = self.get_attack_windup()
                self.attack_cooldown = self.get_reload_time()
        else:
            # Si on est trop loin, on avance
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
        #else:
        #    self._jitter(battle)

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
    def get_attack(self): return 8 
    def get_melee_armor(self): return 2 
    def get_pierce_armor(self): return 2
    def get_range(self): return 0.01 * TILE 
    def get_reload_time(self): return 1.8 
    def get_speed(self): return 1.35 * TILE 
    def get_line_of_sight(self): return 4.0 * TILE 
    def get_symbol(self): return "K" 
    def get_collision_radius(self): return 0.20 * TILE  # 0.5
    def get_attack_windup(self): return 0.15

class Pikeman(Unit):
    def get_max_hp(self): return 55
    def get_attack(self): return 4
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 0.01 * TILE
    def get_reload_time(self): return 3.0
    def get_speed(self): return 1.0 * TILE
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "P"
    def get_collision_radius(self): return 0.15 * TILE  # 0.45
    def get_attack_windup(self): return 0.20

class Crossbowman(Unit):
    def get_max_hp(self): return 35
    def get_attack(self): return 5
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0
    def get_range(self): return 5 * TILE
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "C"
    def get_collision_radius(self): return 0.15 * TILE  # 0.45
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