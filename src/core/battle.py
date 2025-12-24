import time
import random
from typing import List, Dict, Any

from .player import Player
from .map import Map
from .history import add_fight_history 
from .html_generator import generate_snapshot_html

class Battle:
    def __init__(self, players, world_map, logic_dt=0.05, max_time=60.0):
        self.players = players
        self.map = world_map
        self.world_map = world_map
        self.logic_dt = logic_dt
        self.max_time = max_time
        
        # --- CORRECTION ICI : On utilise game_time partout ---
        self.game_time = 0.0 
        
        self.finished = False
        self.winner = None
        self.paused = False
        self.history_saved = False 

        # Infos de départ
        self.start_info = {
            p.name: {
                "ai": p.general.__class__.__name__,
                "unit_count": len(p.squad)
            }
            for p in players
        }

    def export_state_html(self):
        print(f"📸 Snapshot HTML généré à t={self.game_time:.2f}s")
        try:
            generate_snapshot_html(self.players, self.game_time)
            self.paused = True 
        except Exception as e:
            print(f"❌ Erreur HTML : {e}")

    def collect_units(self):
        units = []
        for p in self.players:
            units.extend(p.squad)
        return units

    def force_decision_by_points(self):
        """Calcule les PV restants pour désigner un vainqueur au temps."""
        hp_p1 = sum(u.current_hp for u in self.players[0].squad if u.is_alive)
        hp_p2 = sum(u.current_hp for u in self.players[1].squad if u.is_alive)

        print(f"⌛ TEMPS ÉCOULÉ ! Décision : {self.players[0].name}={int(hp_p1)}HP vs {self.players[1].name}={int(hp_p2)}HP")

        if hp_p1 > hp_p2:
            self.winner = self.players[0]
        elif hp_p2 > hp_p1:
            self.winner = self.players[1]
        else:
            self.winner = None 

    def save_to_history(self):
        """Sauvegarde le résultat dans history.html"""
        if self.history_saved: return
        
        winner_name = self.winner.name if self.winner else "MATCH NUL"
        
        # Liste de tuples : (Symbole, Nom_Equipe)
        survivors_data = []
        for p in self.players:
            for u in p.squad:
                if u.is_alive:
                    survivors_data.append((u.get_symbol(), p.name))
        
        try:
            p1 = self.players[0]
            p2 = self.players[1]
            
            add_fight_history(
                p1.name, 
                p2.name,
                self.start_info[p1.name]['ai'], 
                self.start_info[p2.name]['ai'],
                self.start_info[p1.name]['unit_count'], 
                self.start_info[p2.name]['unit_count'],
                winner_name, 
                self.game_time, # Utilisation correcte de game_time
                survivors_data 
            )
            print(f"✔ Historique sauvegardé : Vainqueur {winner_name}")
            self.history_saved = True
        except Exception as e:
            print("❌ Erreur sauvegarde historique :", e)

    def update(self):
        if self.finished or self.paused:
            return None

        # 1. Vérification du Temps
        self.game_time += self.logic_dt # Incrémentation correcte
        
        if self.game_time >= self.max_time:
            self.force_decision_by_points()
            self.finished = True
            self.save_to_history()
            return self.get_state_dict()

        # 2. Update IA et Unités
        all_units = self.collect_units()
        random.shuffle(all_units) 

        # IA Logic
        for p in self.players:
            units_needing_orders = [u for u in p.squad if u.needs_order()]
            if not units_needing_orders: continue
            try:
                orders = p.general.give_orders(p, self.players, self.map, units_needing_orders)
            except: orders = []

            if orders:
                for order in orders:
                    if order and 'unit' in order and order['unit'].is_alive:
                        u = order['unit']
                        if order['type'] == 'attack': u.set_order('attack', {'target': order.get('target')})
                        elif order['type'] == 'move': u.set_order('move', {'position': order.get('position')})
                        else: u.clear_order()

        # Physique
        for u in all_units:
            if u.is_alive:
                u.update(self, self.logic_dt)

        # Nettoyage
        for p in self.players:
            p.squad = [u for u in p.squad if u.is_alive]

        # 3. Vérification KO
        alive_counts = [len(p.squad) for p in self.players]
        
        if alive_counts[0] == 0 and alive_counts[1] > 0:
            self.winner = self.players[1]
            self.finished = True
        elif alive_counts[1] == 0 and alive_counts[0] > 0:
            self.winner = self.players[0]
            self.finished = True
        elif alive_counts[0] == 0 and alive_counts[1] == 0:
            self.finished = True

        if self.finished:
            self.save_to_history()

        return self.get_state_dict()

    def get_state_dict(self):
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
                        "order": getattr(u, 'current_order', 'None')
                    }
                    for u in p.squad
                ]
            })

        return {
            "players": state_players,
            "game_time": self.game_time,
            "total_time": self.max_time,
            "finished": self.finished,
            "winner": self.winner.name if self.winner else None
        }
