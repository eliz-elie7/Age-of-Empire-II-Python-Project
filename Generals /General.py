from abc import ABC,abstractmethod


class General(ABC):
    "Classe pour tout les généraux AI"
    def __init__(self,name:str):
        self.name = name;
        
    "Methodes partagées"
    def give_orders(self,current_player,all_players,map):
        """current player = armée controlée
        all players = tout le monde pour connaitre les enmmies
        map = carte pour les déplacements"""
        orders = []
      return orders 
        

    def get_name(self):
        return self.name;       