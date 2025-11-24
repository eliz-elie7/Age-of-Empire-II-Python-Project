
class Player:
    """Classe Player - Conteneur des unités et général"""
    
    def __init__(self, name: str, general):
        self.name = name
        self.general = general
        self.squad = []  # Liste de toutes les unités (vivantes + mortes)
    
    def alive_units(self):
        """Retourne les unités vivantes - POUR BATTLE"""
        return [unit for unit in self.squad if unit.is_alive]
    
    def get_alive_units(self):
        """Retourne les unités vivantes - POUR GÉNÉRAUX"""
        return self.alive_units()
    
    def remove_dead_units(self):
        """Nettoie les unités mortes de la squad"""
        self.squad = [unit for unit in self.squad if unit.is_alive]
    
    def add_unit(self, unit):
        """Ajoute une unité au joueur"""
        self.squad.append(unit)
    
    def get_unit_count(self):
        """Retourne le nombre total d'unités (vivantes + mortes)"""
        return len(self.squad)
    
    def get_alive_unit_count(self):
        """Retourne le nombre d'unités vivantes"""
        return len(self.alive_units())