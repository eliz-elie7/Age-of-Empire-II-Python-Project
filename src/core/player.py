class Player:
    """Classe Player - Conteneur des unités et général"""
    
    def __init__(self, name: str, general):
        self.name = name
        self.general = general
        self.squad = []  # Liste de toutes les unités (vivantes + mortes)
    
    def alive_units(self):
        return [unit for unit in self.squad if unit.is_alive]
    
    def get_alive_units(self):
        return self.alive_units()
    
    def remove_dead_units(self):
        self.squad = [unit for unit in self.squad if unit.is_alive]
    
    def add_unit(self, unit):
        self.squad.append(unit)
    
    def get_unit_count(self):
        return len(self.squad)
    
    def get_alive_unit_count(self):
        return len(self.alive_units())
