import math
from enum import Enum
from typing import Optional, Tuple, List

class UnitType(Enum):
    KNIGHT = "knight"
    PIKEMAN = "pikeman"
    CROSSBOWMAN = "crossbowman"

class Player(Enum):
    PLAYER1 = 1
    PLAYER2 = 2

class Unit:
    """Classe de base pour toutes les unités"""
    
    def __init__(self, x: int, y: int, player: Player):
        self.x = x
        self.y = y
        self.player = player
        self.max_hp = self.get_max_hp()
        self.current_hp = self.max_hp
        self.last_attack_time = 0
        self.target: Optional['Unit'] = None
        self.is_alive = True
    
    def get_max_hp(self) -> int:
        """HP maximal selon le type d'unité"""
        raise NotImplementedError
    
    def get_attack(self) -> int:
        """Dégâts de base"""
        raise NotImplementedError
    
    def get_melee_armor(self) -> int:
        """Armure mêlée"""
        raise NotImplementedError
    
    def get_pierce_armor(self) -> int:
        """Armure à distance"""
        raise NotImplementedError
    
    def get_range(self) -> int:
        """Portée d'attaque"""
        raise NotImplementedError
    
    def get_reload_time(self) -> float:
        """Temps de rechargement entre attaques (en secondes)"""
        raise NotImplementedError
    
    def get_speed(self) -> float:
        """Vitesse de déplacement en pixels/seconde"""
        raise NotImplementedError
    
    def get_collision_radius(self) -> float:
        """Retourne le rayon de collision en pixels"""
        raise NotImplementedError
    
    def get_line_of_sight(self) -> int:
        """Ligne de vue"""
        raise NotImplementedError
    
    def get_symbol(self) -> str:
        """Symbole pour affichage terminal"""
        raise NotImplementedError
    
    def get_bonus_damage(self, target: 'Unit') -> int:
        """Dégâts bonus contre certains types d'unités"""
        return 0
    
    def distance_to(self, other: 'Unit') -> float:
        """Distance euclidienne vers une autre unité"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def can_attack(self, target: 'Unit', current_time: float) -> bool:
        """Vérifie si l'unité peut attaquer la cible"""
        if not target.is_alive:
            return False
        if target.player == self.player:
            return False
        if self.distance_to(target) > self.get_range():
            return False
        if current_time - self.last_attack_time < self.get_reload_time():
            return False
        return True
    
    def attack(self, target: 'Unit', current_time: float, battlefield=None) -> int:
        """Attaque une cible et retourne les dégâts infligés"""
        if not self.can_attack(target, current_time):
            return 0
        
        base_damage = self.get_attack()
        bonus_damage = self.get_bonus_damage(target)
        total_attack = base_damage + bonus_damage
        
        # Appliquer l'armure appropriée
        if self.get_range() > 0:  # Attaque à distance
            armor = target.get_pierce_armor()
        else:  # Attaque mêlée
            armor = target.get_melee_armor()
        
        # Formule AOE2: max(1, attack - armor)
        final_damage = max(1, total_attack - armor)
        
        target.take_damage(final_damage, battlefield)
        self.last_attack_time = current_time
        
        return final_damage
    
    def take_damage(self, damage: int, battlefield=None):
        """Prend des dégâts"""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            if self.is_alive:  # Si c'était vivant et maintenant mort
                if battlefield:
                    battlefield.register_death(self.x, self.y)
            self.is_alive = False
    
    def move_towards(self, target_x: int, target_y: int):
        """Se déplace vers une position (simple, 1 case à la fois)"""
        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1
        
        if self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1


class Pikeman(Unit):
    """Piquier - Infanterie anti-cavalerie"""
    
    def get_max_hp(self) -> int:
        return 55
    
    def get_attack(self) -> int:
        return 4
    
    def get_melee_armor(self) -> int:
        return 0
    
    def get_pierce_armor(self) -> int:
        return 0
    
    def get_range(self) -> int:
        return 1  # Mêlée
    
    def get_reload_time(self) -> float:
        return 3.0
    
    def get_speed(self) -> float:
        return 1.0
    
    def get_line_of_sight(self) -> int:
        return 4
    
    def get_symbol(self) -> str:
        """Symbole pour affichage terminal"""
        return 'P'
    
    def get_bonus_damage(self, target: Unit) -> int:
        """Bonus massif contre cavalerie"""
        if isinstance(target, Knight):
            return 22 # Bonus anti-cavalerie
        return 0



def create_unit(unit_type: UnitType, x: int, y: int, player: Player) -> Unit:
    """Factory pour créer une unité"""
    if unit_type == UnitType.PIKEMAN:
        return Pikeman(x, y, player)
    else:
        raise ValueError(f"Type d'unité inconnu: {unit_type}")