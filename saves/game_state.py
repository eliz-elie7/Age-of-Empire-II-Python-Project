# game_state.py
# Conteneur global pour sauvegarder et restaurer une bataille complète

from typing import Optional
from battle import Battle


class GameState:
    """
    GameState contient TOUT l'état d'une bataille en cours.

    Il encapsule l'objet Battle afin de pouvoir :
    - sauvegarder la partie
    - restaurer la simulation
    - accéder aux infos principales simplement
    """

    def __init__(self, battle: Battle, scenario_name: Optional[str] = None):
        # Moteur principal de la bataille
        self.battle = battle

        # Nom du scénario (optionnel)
        self.scenario_name = scenario_name

    # ----------------------------
    # PROPRIÉTÉS UTILES
    # ----------------------------

    @property
    def time(self):
        """Retourne le temps actuel de la bataille."""
        return self.battle.time

    @property
    def finished(self):
        """Retourne True si la bataille est terminée."""
        return self.battle.finished

    @property
    def winner(self):
        """Retourne le gagnant s'il existe."""
        return self.battle.winner

    # ----------------------------
    # UPDATE PRINCIPAL
    # ----------------------------

    def update(self, delta_time=None):
        """
        Fait avancer la bataille en appelant Battle.update().
        """
        return self.battle.update(delta_time)

    # ----------------------------
    # RESET
    # ----------------------------

    def reset(self):
        """Réinitialise complètement la bataille."""
        self.battle.reset()

    # ----------------------------
    # DEBUG
    # ----------------------------

    def __repr__(self):
        return (
            f"GameState("
            f"scenario={self.scenario_name}, "
            f"time={self.time:.2f}, "
            f"finished={self.finished}, "
            f"winner={self.winner.name if self.winner else None}"
            f")"
        )
