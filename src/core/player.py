class Player:
    """Conteneur des unités et du général"""

    def __init__(self, name: str, general):
        self.name = name
        self.general = general() if isinstance(general, type) else general
        self.color = None
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
