# battle.py
import time
import random
from .player import Player
from .units import Unit
from .map import Map
from typing import List, Dict, Any

class Battle:
    def __init__(self, players, world_map, logic_dt=0.05, max_time=60.0):
        self.players = players
        self.map = world_map
        self.world_map = world_map  # alias attendu par certains composants
        self.logic_dt = logic_dt
        self.max_time = max_time
        self.time = 0.0
        self.finished = False
        self.winner = None

    def collect_units(self):
        units = []
        for p in self.players:
            units.extend(p.squad)
        return units

    def all_units(self):
        """Retourne toutes les unités vivantes du champ de bataille"""
        return [u for u in self.collect_units() if getattr(u, 'is_alive', False)]

    def update(self):
        if self.finished:
            return None

        # Avancement du temps
        self.time += self.logic_dt
        if self.time >= self.max_time:
            self.finished = True

        all_units = self.collect_units()

        # ===============================
        #     IA – Donner des ordres
        # ===============================
        for p in self.players:
            units_needing_orders = [u for u in p.squad if u.needs_order()]
            # Récupère les ordres depuis le général
            orders = p.general.give_orders(p, self.players, self.map, units_needing_orders)
            if not orders:
                continue

            # Applique les ordres retournés
            for order in orders:
                if not order or 'type' not in order or 'unit' not in order:
                    continue
                u = order['unit']
                # Sécurité : vérifier que l'unité est encore vivante et appartient bien au joueur courant
                if not getattr(u, 'is_alive', False):
                    continue
                # Appliquer selon le type
                if order['type'] == 'attack' and 'target' in order:
                    u.set_order('attack', {'target': order['target']})
                elif order['type'] == 'move' and 'position' in order:
                    u.set_order('move', {'position': order['position']})
                elif order['type'] == 'hold':
                    # On pose un ordre "hold" (n'empêche pas le clear_order d'être appelé plus tard)
                    u.set_order('hold', {})
                else:
                    # ordre inconnu -> clear
                    u.clear_order()

        # ===============================
        #     Mise à jour des unités
        # ===============================
        for u in all_units:
            u.update(self, self.logic_dt)

        # ===============================
        #     Nettoyage des morts
        # ===============================
        for p in self.players:
            p.squad = [u for u in p.squad if u.is_alive]

        # ===============================
        #     Victoire
        # ===============================
        alive_players = [p for p in self.players if len([u for u in p.squad if u.is_alive]) > 0]
        if len(alive_players) == 1:
            self.finished = True
            self.winner = alive_players[0]

        # ===============================
        #     Construction du STATE
        # ===============================
        state_players = []
        for p in self.players:
            state_players.append({
                "name": p.name,
                "alive_units": len([u for u in p.squad if u.is_alive]),
                "units": [
                    {
                        "symbol": u.get_symbol(),
                        "x": u.x,
                        "y": u.y,
                        "hp": u.current_hp,
                        "order": u.current_order
                    }
                    for u in p.squad
                ]
            })

        return {
            "players": state_players,
            "game_time": self.time,
            "total_time": self.max_time,
            "finished": self.finished,
            "winner": self.winner.name if self.winner else None
        }
