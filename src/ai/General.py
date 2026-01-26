from abc import ABC, abstractmethod

class General(ABC):
    """Classe abstraite pour tous les généraux IA"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def give_orders(self, current_player, all_players, map, units_needing_orders):
        """Méthode principale où le général prend ses décisions
        
        Args:
            current_player: Le joueur que ce général contrôle
            all_players: Liste de tous les joueurs de la bataille
            map: La carte de jeu pour les déplacements
            units_needing_orders: Liste des unités qui ont besoin de nouveaux ordres
            
        Returns:
            Liste d'ordres à exécuter
        """
        pass

    def get_name(self) -> str:
        return self.name
