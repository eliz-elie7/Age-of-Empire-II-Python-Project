# src/core/units.py

import math
from enum import Enum
from random import random
from typing import Optional, Tuple, List

# NOTE: On expose une échelle TILE => pixels par "tile" (inspirée AoE)
TILE = 32.0  # 1 tile = 32 pixels (ajustable)

class UnitType(Enum):
    KNIGHT = "knight"
    PIKEMAN = "pikeman"
    CROSSBOWMAN = "crossbowman"

class Unit:
    """Classe de base pour toutes les unités - Version RTS complète"""

    def __init__(self, x: float, y: float, player):
        # player est un objet Player

        # Position en pixels (FLOAT)
        self.x = x
        self.y = y
        self.player = player  # Référence à l'objet Player propriétaire

        # Stats de base
        self.max_hp = self.get_max_hp()
        self.current_hp = self.max_hp
        self.is_alive = True

        # Système d'ordres RTS
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True
        self.attack_cooldown = 0.0
        self.attack_windup_timer = 0.0
    # ===== MÉTHODES ABSTRAITES =====

    def get_max_hp(self) -> int:
        raise NotImplementedError

    def get_attack(self) -> int:
        raise NotImplementedError

    def get_melee_armor(self) -> int:
        raise NotImplementedError

    def get_pierce_armor(self) -> int:
        raise NotImplementedError

    def get_range(self) -> float:
        raise NotImplementedError

    def get_reload_time(self) -> float:
        raise NotImplementedError

    def get_speed(self) -> float:
        raise NotImplementedError

    def get_line_of_sight(self) -> float:
        raise NotImplementedError

    def get_symbol(self) -> str:
        raise NotImplementedError

    def get_collision_radius(self) -> float:
        raise NotImplementedError

    def can_occupy_same_space(self, other: 'Unit') -> bool:
        return False
    def get_attack_windup(self) -> float:
        # Retourne un windup par défaut (en secondes)
        return 0.12

    # ===== GESTION DES STATS ET DÉGÂTS =====

    def take_damage(self, damage: int, damage_type: str = "melee"):
        if not self.is_alive:
            return

        if damage_type == "melee":
            armor = self.get_melee_armor()
        elif damage_type == "pierce":
            armor = self.get_pierce_armor()
        else:
            armor = 0

        final_damage = max(0, damage - armor)
        self.current_hp -= final_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            self.clear_order()

    # ===== GESTION DES ORDRES =====

    def set_order(self, order_type: str, data: dict):
        """Définit un nouvel ordre"""
        self._current_order = order_type
        self._order_data = data
        self.needs_new_orders = False

    def clear_order(self):
        """Annule l'ordre actuel"""
        self._current_order = None
        self._order_data = {}
        self.needs_new_orders = True
    def needs_order(self) -> bool:
        """Vérifie si l'unité a besoin d'un nouvel ordre"""
        return self.needs_new_orders   

    @property
    def current_order(self):
        """Retourne le type d'ordre pour la visualisation"""
        return self._current_order

    # ===== LOGIQUE DE MISE À JOUR =====

    def update(self, battle, delta_time: float):
        """Mise à jour à chaque pas de temps"""

        if not self.is_alive:
            return
        # 1. Mise à jour du cooldown d'attaque
        self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
        # 2. Mise à jour du windup
        if self.attack_windup_timer > 0:
            self.attack_windup_timer -= delta_time
            if self.attack_windup_timer <= 0:
                target = self._order_data.get('target')
                if target and target.is_alive:
                    target.take_damage(self.get_attack(), damage_type="melee") 
            return 

        # 2. Exécution de l'ordre actuel
        if self._current_order == 'move':
            self._execute_move_order(delta_time, battle)
        elif self._current_order == 'attack':
            self._execute_attack_order(delta_time, battle)
        # L'ordre 'hold' ne fait rien (pas de mouvement, pas d'attaque)

    def _execute_move_order(self, delta_time: float, battle):
        """Exécute l'ordre de mouvement vers une position (x, y)"""
        if 'position' not in self._order_data:
            self.clear_order()
            return

        target_x, target_y = self._order_data['position']

        # Tenter de se déplacer vers la position cible
        self.move_toward(target_x, target_y, delta_time, battle)

        # Vérifier si la position est atteinte
        if self.has_reached_position(target_x, target_y):
            self.clear_order()

    def _execute_attack_order(self, delta_time: float, battle):
        """Exécute l'ordre d'attaque sur une cible (Unit)"""
        if 'target' not in self._order_data:
            self.clear_order()
            return

        target = self._order_data['target']

        if not target.is_alive:
            self.clear_order()
            return

        distance = self.distance_to(target)

        if distance <= self.get_range():
            # 1. Attaque si à portée et rechargement terminé
            if self.attack_cooldown <= 0:
                #target.take_damage(self.get_attack(), damage_type="melee")
                # Assumé "melee" pour l'instant
                self.attack_windup_timer = self.get_attack_windup()
                self.attack_cooldown = self.get_reload_time()

        else:
            # 2. Sinon, se déplacer vers la cible
            self.move_toward(target.x, target.y, delta_time, battle)

    # ===== MÉTHODES DE MOUVEMENT ET DE DISTANCE =====

    def distance_to(self, other: 'Unit') -> float:
        """Calcule la distance au centre d'une autre unité"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def has_reached_position(self, target_x: float, target_y: float, margin: float = 5.0) -> bool:
        """Vérifie si la position cible est atteinte (dans une marge)"""
        dist_sq = (self.x - target_x)**2 + (self.y - target_y)**2
        return dist_sq <= margin**2

    def move_toward(self, target_x: float, target_y: float, delta_time: float, battle):
        """Déplace l'unité vers la position (target_x, target_y)"""

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < 0.1:  # Déjà très proche ou sur la cible
            return

        # Vitesse de déplacement maximum pour ce pas de temps
        move_distance = min(self.get_speed() * delta_time, distance)

        # Calcul des nouvelles coordonnées
        next_x = self.x + (dx / distance) * move_distance
        next_y = self.y + (dy / distance) * move_distance

        # Vérification des collisions via la carte
        world_map = getattr(battle, 'map', None) or getattr(battle, 'world_map', None)
        all_units = None
        if hasattr(battle, 'all_units') and callable(getattr(battle, 'all_units')):
            all_units = battle.all_units()
        elif hasattr(battle, 'collect_units') and callable(getattr(battle, 'collect_units')):
            all_units = battle.collect_units()

        if world_map is None or all_units is None or world_map.can_move_to(self, next_x, next_y, all_units):
            self.x = next_x
            self.y = next_y

# ===== IMPLÉMENTATIONS DES UNITÉS =====
# Les valeurs "brutes" (tiles, hp, attack...) sont basées sur références type AoE2,
# converties en pixels pour speed/range/los/collision_radius.

class Knight(Unit):
    def get_max_hp(self) -> int: return 100
    def get_attack(self) -> int: return 10
    def get_melee_armor(self) -> int: return 2
    def get_pierce_armor(self) -> int: return 2
    def get_range(self) -> float: return 1.0 * TILE                # melee ~ 1 tile
    def get_reload_time(self) -> float: return 1.5
    def get_speed(self) -> float: return 1.35 * TILE               # tiles/sec -> px/sec
    def get_line_of_sight(self) -> float: return 6.0 * TILE       # vision ~ 6 tiles
    def get_symbol(self) -> str: return 'K'
    def get_collision_radius(self) -> float: return 0.5 * TILE    # 0.5 tile radius
    def get_attack_windup(self) -> float: return 0.15

class Pikeman(Unit):
    def get_max_hp(self) -> int: return 55
    def get_attack(self) -> int: return 4
    def get_melee_armor(self) -> int: return 0
    def get_pierce_armor(self) -> int: return 0
    def get_range(self) -> float: return 1.0 * TILE
    def get_reload_time(self) -> float: return 3.0
    def get_speed(self) -> float: return 1.0 * TILE
    def get_line_of_sight(self) -> float: return 5.0 * TILE
    def get_symbol(self) -> str: return 'P'
    def get_collision_radius(self) -> float: return 0.45 * TILE
    def get_attack_windup(self) -> float: return 0.20

class Crossbowman(Unit):
    def get_max_hp(self) -> int: return 35
    def get_attack(self) -> int: return 6
    def get_melee_armor(self) -> int: return 0
    def get_pierce_armor(self) -> int: return 1
    def get_range(self) -> float: return 4.5 * TILE               # ~4.5-5 tiles
    def get_reload_time(self) -> float: return 2.0
    def get_speed(self) -> float: return 0.96 * TILE
    def get_line_of_sight(self) -> float: return 8.0 * TILE
    def get_symbol(self) -> str: return 'C'
    def get_collision_radius(self) -> float: return 0.45 * TILE
    def get_attack_windup(self) -> float: return 0.30

# ===== FACTORY =====

def create_unit(unit_type: UnitType, x: float, y: float, player) -> Unit:
    if unit_type == UnitType.KNIGHT:
        return Knight(x, y, player)
    elif unit_type == UnitType.PIKEMAN:
        return Pikeman(x, y, player)
    elif unit_type == UnitType.CROSSBOWMAN:
        return Crossbowman(x, y, player)
    else:
        raise ValueError(f"Type d'unité inconnu: {unit_type}")
