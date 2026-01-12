class Player:
    """Conteneur des unités et du général"""

    # J'ai ajouté le paramètre color="blue" par défaut
    def __init__(self, name: str, general, color: str = "blue"):
        self.name = name
        self.general = general
        self.color = color  # <--- C'est la ligne qui manquait pour corriger l'erreur
        self.squad = []

    def alive_units(self):
        return [u for u in self.squad if getattr(u, "is_alive", False)]

    def get_alive_units(self):
        return self.alive_units()

    def remove_dead_units(self):
        self.squad = [u for u in self.squad if getattr(u, "is_alive", False)]

    def add_unit(self, unit):
        self.squad.append(unit)

    def get_unit_count(self):
        return len(self.squad)

    def get_alive_unit_count(self):
        return len(self.alive_units())