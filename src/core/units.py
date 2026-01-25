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
    # --- AJOUTS ---
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
        
        # Reference battle (assignée dans update)
        self.battle = None

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

    # ===== LOGIQUE DE DÉGÂTS (A.D + CHEF) =====

    def get_bonus_damage(self, target: 'Unit') -> int:
        """Par défaut, aucun bonus"""
        return 0

    def get_damage_type(self) -> str:
        """Par défaut, tout le monde tape en mêlée sauf surcharge."""
        return "melee"

    def get_total_damage(self, target: 'Unit') -> int:
        """Calcul neutre : Attaque de base + Bonus éventuel."""
        return self.get_attack() + self.get_bonus_damage(target)

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

    # ===== UPDATE & COMBAT (FUSIONNÉ) =====

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
            # 1. Calcul des dégâts de base (DIALLO : Base + Bonus - Armure)
            # On récupère le bon type d'armure de la cible selon notre type d'attaque
            dmg_type = self.get_damage_type()
            raw_damage = self.get_total_damage(target)
            
            target_armor = target.get_melee_armor() if dmg_type == "melee" else target.get_pierce_armor()
            base_dmg = max(1, raw_damage - target_armor)
            
            # 2. Logique de Hauteur (CHEF)
            # +25% damage when attacking from higher elevation (AOE2 Rule)
            # (Le code du chef mettait 1.3/0.8, on peut garder ou ajuster à 1.25 strict AOE2)
            if self.battle:
                my_el = self.battle.world_map.get_elevation_at(self.x, self.y)
                target_el = self.battle.world_map.get_elevation_at(target.x, target.y)
                
                final_dmg = base_dmg
                if my_el > target_el:
                    final_dmg = int(base_dmg * 1.25) # +25% AOE2 Standard
                elif my_el < target_el:
                    final_dmg = int(base_dmg * 0.75) # -25% AOE2 Standard
            else:
                final_dmg = base_dmg

            # 3. Application
            # On appelle take_damage avec 0 armure car on l'a déjà déduite ci-dessus
            # Ou mieux : on passe les dégâts bruts modifiés et le type, et take_damage refait le calcul ?
            # Pour respecter la logique du chef qui calcule tout ici, on applique directement aux HP :
            target.current_hp -= max(1, final_dmg) 
            if target.current_hp <= 0:
                target.current_hp = 0
                target.is_alive = False
                target.clear_order()
            
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
                # --- LOGIQUE D'ÉLÉVATION (CHEF) ---
                current_el = battle.world_map.get_elevation_at(self.x, self.y)
                target_el = battle.world_map.get_elevation_at(target_pos[0], target_pos[1])
                
                speed_mod = 1.0
                if target_el > current_el:
                    speed_mod = 0.6  # Ralentissement en montée
                elif target_el < current_el:
                    speed_mod = 1.2  # Bonus en descente

                vx = (dx / dist) * self.get_speed() * speed_mod
                vy = (dy / dist) * self.get_speed() * speed_mod

        # --- B. SÉPARATION (CHEF) ---
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
        
        # On garde une référence à battle pour le calcul des dégâts
        self.battle = battle 

        self.attack_cooldown = max(0.0, self.attack_cooldown - delta_time)

        # 1. SI EN WINDUP
        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0:
                self._apply_combat_damage()
            return

        # 2. VÉRIFICATION DE LA CIBLE
        if self._current_order == "attack":
            target = self._order_data.get("target")
            if not target or not target.is_alive:
                self.clear_order()
                return

            dist = self.distance_to(target)
            
            # BONUS DE PORTÉE : Les unités en hauteur voient plus loin / tirent plus loin
            my_el = battle.world_map.get_elevation_at(self.x, self.y)
            range_bonus = 15.0 if my_el > 0 else 0.0
            
            eff_range = (self.get_range() + range_bonus + self.get_collision_radius() + target.get_collision_radius()) + 5.0
            
            if dist <= eff_range:
                if self.attack_cooldown <= 0:
                    self.attack_windup_timer = self.get_attack_windup()
                    return 
                else:
                    return 

        # 3. MOUVEMENT (can_move_to contient maintenant le test de falaise)
        vx, vy = self._compute_steering(battle)

        if vx != 0 or vy != 0:
            nx = self.x + vx * delta_time
            ny = self.y + vy * delta_time
            all_units = battle.all_units()
            
            # Ici can_move_to va renvoyer False si la pente est > 1
            if battle.world_map.can_move_to(self, nx, ny, all_units):
                self.x, self.y = battle.world_map.clamp_position(nx, ny)
            if not battle.world_map.can_move_to(self, nx, ny, all_units):
                # Si on ne peut pas monter, on essaie de bouger uniquement sur l'axe X ou Y 
                # pour longer la colline au lieu de s'arrêter net.
                if battle.world_map.can_move_to(self, nx, self.y, all_units):
                    self.x = nx
                elif battle.world_map.can_move_to(self, self.x, ny, all_units):
                    self.y = ny

    # ===== ORDRES (Structure Chef conservée) =====

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

# ===== UNITÉS (IMPLEMENTATION DIALLO + AJUSTEMENTS COLLISION CHEF) =====

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
    def get_collision_radius(self): return 0.20 * TILE # Ajusté pour éviter bouchons
    def get_attack_windup(self): return 0.15
    
    def get_bonus_damage(self, target: 'Unit') -> int:
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
    def get_collision_radius(self): return 0.15 * TILE
    def get_attack_windup(self): return 0.20
    
    def get_bonus_damage(self, target: 'Unit') -> int:
        if isinstance(target, Knight): 
            return 22
        return 0

class Crossbowman(Unit):
    def get_max_hp(self): return 35
    def get_attack(self): return 6
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 0 # 0 dans AOE2 Castle Age
    def get_range(self): return 5.0 * TILE # Augmenté un peu pour compenser la carte
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "C"
    def get_collision_radius(self): return 0.15 * TILE
    def get_attack_windup(self): return 0.30
    
    def get_damage_type(self) -> str:
        return "pierce"

class LongSwordsman(Unit):
    def get_max_hp(self): return 60
    def get_attack(self): return 9
    def get_melee_armor(self): return 1
    def get_pierce_armor(self): return 1
    def get_range(self): return 0.5 * TILE
    def get_reload_time(self): return 2.0
    def get_speed(self): return 0.9 * TILE
    def get_line_of_sight(self): return 4.0 * TILE
    def get_symbol(self): return "S"
    def get_collision_radius(self): return 0.15 * TILE

class EliteSkirmisher(Unit):
    def get_max_hp(self): return 30
    def get_attack(self): return 2 # +3 vs Pikeman, +4 vs Archer
    def get_melee_armor(self): return 0
    def get_pierce_armor(self): return 4
    def get_range(self): return 5.0 * TILE
    def get_reload_time(self): return 3.0
    def get_speed(self): return 0.96 * TILE
    def get_line_of_sight(self): return 7.0 * TILE
    def get_symbol(self): return "E"
    def get_collision_radius(self): return 0.15 * TILE

    def get_damage_type(self) -> str:
        return "pierce"

    def get_bonus_damage(self, target: 'Unit') -> int:
        if isinstance(target, (LongSwordsman, Pikeman)):
            return 3
        if isinstance(target, (Crossbowman, EliteSkirmisher)):
            return 4
        return 0

# ===== FACTORY =====

def create_unit(unit_type: UnitType, x: float, y: float, player) -> Unit:
    if unit_type == UnitType.KNIGHT:
        return Knight(x, y, player)
    if unit_type == UnitType.PIKEMAN:
        return Pikeman(x, y, player)
    if unit_type == UnitType.CROSSBOWMAN:
        return Crossbowman(x, y, player)
    if unit_type == UnitType.LONGSWORDSMAN:
        return LongSwordsman(x, y, player)
    if unit_type == UnitType.ELITESKIRMISHER:
        return EliteSkirmisher(x, y, player)
        
    raise ValueError(f"Type d'unité inconnu: {unit_type}")