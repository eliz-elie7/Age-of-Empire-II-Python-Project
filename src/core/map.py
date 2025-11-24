class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Dictionnaire : unit -> (x, y)
        self.units = {}

    # ----- Dimensions -----
    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    # ----- Gestion des positions -----
    def is_within_bounds(self, x, y):
        """
        Vérifie si une position est dans les limites de la carte.
        Les positions peuvent être flottantes.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def get_units_at(self, x, y, tol=1e-6):
        """
        Retourne la liste des unités dont la position
        est (approximativement) égale à (x, y).
        Comme les coordonnées sont flottantes, on utilise une tolérance.
        """
        result = []
        for unit, (ux, uy) in self.units.items():
            if abs(ux - x) <= tol and abs(uy - y) <= tol:
                result.append(unit)
        return result

    def is_position_free(self, x, y):
        """
        Vrai si aucune unité n'occupe (en gros) cette position.
        """
        return len(self.get_units_at(x, y)) == 0

    # ----- Gestion des unités -----
    def get_all_units(self):
        """Retourne toutes les unités présentes sur la carte."""
        return list(self.units.keys())

    def register_unit_movement(self, unit, new_x, new_y):
        """
        Met à jour la position d'une unité.
        - Lève une erreur si l'unité n'existe pas
        - Vérifie que la position est dans les limites
        """
        if unit not in self.units:
            raise ValueError("Unité inconnue : impossible de la déplacer.")

        if not self.is_within_bounds(new_x, new_y):
            raise ValueError("Position hors limites : mouvement impossible.")

        self.units[unit] = (new_x, new_y)

    def register_unit_death(self, unit):
        """
        Retire une unité de la carte.
        """
        if unit in self.units:
            del self.units[unit]

    # ----- Optionnel : ajouter une unité -----
    def add_unit(self, unit, x, y):
        """
        Ajoute une unité sur la carte (optionnel pour faciliter les tests).
        """
        if not self.is_within_bounds(x, y):
            raise ValueError("Position hors limites.")
        self.units[unit] = (x, y)
