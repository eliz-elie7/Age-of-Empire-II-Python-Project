import time
import random
import math

class Battle:
    def __init__(self, players, world_map=None, dt=0.1, max_turns=1000, log=True):
        self.players = players
        self.world_map = world_map
        self.dt = dt
        self.max_turns = max_turns
        self.log = log
        
        # État du jeu
        self.turn = 0
        self.game_time = 0.0
        self.finished = False
        self.winner = None
        self.history = []

    def step(self):
        """Exécute une frame de simulation"""
        self.turn += 1
        self.game_time += self.dt

        # PHASE 1: Ordres pour unités qui en ont besoin
        all_orders = []
        for player in self.players:
            units_needing_orders = [u for u in player.alive_units() if u.needs_new_orders]
            
            if units_needing_orders:
                orders = player.general.give_orders(player, self.players, self.world_map, units_needing_orders)
                all_orders.extend(orders)

        
        # PHASE 2: Assigner les ordres aux unités
        random.shuffle(all_orders)
        for order in all_orders:
            unit = order['unit']
            params = {}
             for k, v in order.items():
               if k != "unit" and k != "type":
                  params[k] = v
        
        # PHASE 3: Mise à jour des unités
        for player in self.players:
            for unit in player.alive_units():
                unit.update(self, self.dt)

        
        # PHASE 4: Nettoyage des unités mortes
        for player in self.players:
            player.remove_dead_units()

        self._check_end_condition()

    def _check_end_condition(self):
        """Vérifie si la bataille est terminée"""
        alive_players = [p for p in self.players if len(p.alive_units()) > 0]
        
        if len(alive_players) <= 1:
            self.finished = True
            self.winner = alive_players[0] if alive_players else None
        elif self.turn >= self.max_turns:
            self.finished = True

    def run(self):
        """Boucle principale RTS"""
        start_time = time.time()
        last_tick = start_time
        
        while not self.finished:
            current_time = time.time()
            elapsed = current_time - last_tick
            
            if elapsed >= self.dt:
                self.step()
                last_tick = current_time
            
            time.sleep(0.001)
        
        end_time = time.time()
        return end_time - start_time

    def all_units(self):
        """Retourne toutes les unités vivantes"""
        units = []
        for player in self.players:
            units.extend(player.alive_units())
        return units

    def get_game_state(self):
        """Retourne l'état du jeu pour la visualisation"""
        return {
            'game_time': self.game_time,
            'turn': self.turn,
            'players': [
                {
                    'name': p.name,
                    'alive_units': len(p.alive_units()),
                    'units': [(u.x, u.y, u.get_symbol()) for u in p.alive_units()]
                }
                for p in self.players
            ],
            'finished': self.finished,
            'winner': self.winner.name if self.winner else None
        }