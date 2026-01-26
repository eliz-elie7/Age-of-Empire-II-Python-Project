from .General import General

class King_Julian(General):

    def __init__(self):
        super().__init__("King_Julian")
    def __init__(self, team_name):
        self.team = team_name
        self.strategy = "UNDECIDED"
        self.groups = {"frontline": [], "flank": []}

    def analyze_and_decide(self, my_units, enemy_units):
        # Comptage des types d'unités
        archers = [u for u in my_units if u.unit_type == "ARCHER"]
        infantry = [u for u in my_units if u.unit_type == "INFANTRY"]
        cavalry = [u for u in my_units if u.unit_type == "CAVALRY"]
        
        # CRITÈRE : Si + de 60% d'archers -> Harcèlement
        if len(archers) > (len(my_units) * 0.6):
            self.strategy = "HARASSMENT"
            self.groups["frontline"] = my_units # Tout le monde harcèle
            
        # CRITÈRE : Si présence de cavalerie et d'infanterie -> Marteau et Enclume
        elif len(cavalry) > 0 and len(infantry) > 0:
            self.strategy = "HAMMER_AND_ANVIL"
            self.groups["frontline"] = infantry # L'Enclume
            self.groups["flank"] = cavalry      # Le Marteau
            
        else:
            self.strategy = "DEFENSIVE"

        print(f"--- Stratégie adoptée par {self.team}: {self.strategy} ---")

    def issue_orders(self, enemy_base_pos):
        if self.strategy == "HARASSMENT":
            for u in self.groups["frontline"]:
                # Ordre : Aller à portée de tir, tirer, reculer (Hit & Run)
                u.set_objective("HIT_AND_RUN", enemy_base_pos)

        elif self.strategy == "HAMMER_AND_ANVIL":
            # L'enclume avance de front
            for u in self.groups["frontline"]:
                u.set_objective("HOLD_LINE", enemy_base_pos)
            # Le marteau contourne (on ajoute un décalage sur l'axe Y pour le flanc)
            flank_pos = (enemy_base_pos[0], enemy_base_pos[1] + 5)
            for u in self.groups["flank"]:
                u.set_objective("FLANK_ATTACK", flank_pos)
