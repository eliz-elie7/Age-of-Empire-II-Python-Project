from abc import ABC, abstractmethod

class View(ABC):
    """
    Classe abstraite pour toutes les vues (Terminal, Isometric, etc.).
    """

    def __init__(self):
        self._running = True            # ← MANQUAIT !
        self._switch_requested = False  # déjà présent

    def request_switch(self):
        """Appelé quand la vue veut passer à une autre vue (ex: appui F9)."""
        self._switch_requested = True
    
    def is_running(self) -> bool:
        """Indique si la vue souhaite rester active."""
        return self._running            # maintenant OK

    def stop(self):
        """Demande l'arrêt de la vue (ex: quitter l'application)."""
        self._running = False

    def wants_switch(self) -> bool:
        """main.py lira ceci à chaque frame."""
        return self._switch_requested

    @abstractmethod
    def on_enter(self, battle, game_state):
        pass

    @abstractmethod
    def render(self, game_state):
        pass

    @abstractmethod
    def handle_input(self, key):
        pass

    @abstractmethod
    def on_exit(self):
        pass
