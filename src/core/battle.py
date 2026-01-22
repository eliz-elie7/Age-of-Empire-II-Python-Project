# src/core/battle.py

import math
from typing import List, Dict, Any, Optional


class Battle:
    """
    Moteur de simulation RTS indépendant de la visualisation.
    """

    def __init__(
        self,
        players: List,
        world_map,
        logic_dt: float = 0.05,
        max_time: float = 60.0
    ):
        self.players = players
        self.map = world_map
        self.world_map = world_map  # alias
        self.logic_dt = logic_dt
        self.max_time = max_time

        self.time = 0.0
        self.finished = False
        self.winner = None
        self.step_count = 0

    # --------------------------------------------------
    # UNITÉS
    # --------------------------------------------------

    def collect_units(self) -> List:
        units = []
        for p in self.players:
            units.extend(p.squad)
        return units

    def all_units(self) -> List:
        return [u for u in self.collect_units() if getattr(u, "is_alive", False)]

    # --------------------------------------------------
    # UPDATE PRINCIPALE
    # --------------------------------------------------

    def update(self, delta_time: Optional[float] = None) -> Optional[Dict[str, Any]]:
        if self.finished:
            return None

        dt = self.logic_dt if delta_time is None else float(delta_time)
        self.time += dt
        self.step_count += 1

        if self.time >= self.max_time:
            self.finished = True

        # Snapshot vivant au début du tick
        all_units = self.all_units()

        # ===============================
        # 1) IA — attribution des ordres
        # ===============================
        for p in self.players:
            units_needing_orders = [
                u for u in p.squad
                if getattr(u, "needs_order", lambda: True)()
            ]

            if not units_needing_orders:
                continue

            orders = []
            if hasattr(p, "general") and hasattr(p.general, "give_orders"):
                try:
                    orders = p.general.give_orders(
                        p,
                        self.players,
                        self.map,
                        units_needing_orders
                    )
                except Exception:
                    orders = []

            for order in orders or []:
                if not order or "type" not in order or "unit" not in order:
                    continue

                u = order["unit"]
                if not getattr(u, "is_alive", False):
                    continue

                if order["type"] == "attack" and "target" in order:
                    u.set_order("attack", {"target": order["target"]})
                elif order["type"] == "move" and "position" in order:
                    u.set_order("move", {"position": order["position"]})
                elif order["type"] == "hold":
                    u.set_order("hold", {})
                else:
                    u.clear_order()

        # ===============================
        # 2) UPDATE DES UNITÉS
        # ===============================
        for u in all_units:
            if hasattr(u, "update"):
                try:
                    u.update(self, dt)
                except Exception:
                    # sécurité absolue
                    u.is_alive = False

        # ===============================
        # 3) CLAMP GLOBAL (ANTI COORD NÉGATIVES)
        # ===============================
        for u in self.all_units():
            u.x, u.y = self.world_map.clamp_position(u.x, u.y)

        # ===============================
        # 4) NETTOYAGE DES MORTS
        # ===============================
        for p in self.players:
            #p.squad = [u for u in p.squad if getattr(u, "is_alive", False)]
            p.squad = [u for u in p.squad if u.current_hp > 0]

        # ===============================
        # 5) CONDITION DE VICTOIRE
        # ===============================
        alive_players = [
            p for p in self.players
            if any(u.current_hp > 0 for u in p.squad)
        ]

        if len(alive_players) == 1:
            self.finished = True
            self.winner = alive_players[0]

        # ===============================
        # 6) SNAPSHOT
        # ===============================
        return self.get_state()

    # --------------------------------------------------
    # STATE
    # --------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        state_players = []

        for p in self.players:
            units_state = []
            for u in p.squad:
                units_state.append({
                    "id": id(u),
                    "symbol": u.get_symbol(),
                    "x": float(u.x),
                    "y": float(u.y),
                    "hp": float(u.current_hp),
                    "order": u.current_order,
                    "state": (
                        "dead" if not u.is_alive
                        else u.current_order or "idle"
                    )
                })

            state_players.append({
                "name": p.name,
                "color": p.color,
                "alive_units": len([u for u in p.squad if u.current_hp > 0]),
                "units": units_state
            })

        return {
            "players": state_players,
            "game_time": float(self.time),
            "total_time": float(self.max_time),
            "finished": bool(self.finished),
            "winner": self.winner.name if self.winner else None,
            "_step": self.step_count
        }

    # --------------------------------------------------
    # UTILITAIRE
    # --------------------------------------------------

    def reset(self):
        self.time = 0.0
        self.finished = False
        self.winner = None
        self.step_count = 0
    def get_result(self):
        """
        Résumé final pour la CLI / plotting
        """
        result = {
            "time": self.time,
            "max_time": self.max_time,
            "finished": self.finished,
            "winner": self.winner.name if self.winner else None,
            "players": []
        }

        for p in self.players:
            total = len(p.squad)
            alive = len([u for u in p.squad if u.current_hp > 0])

            result["players"].append({
                "name": p.name,
                "alive_units": alive,
                "dead_units": total - alive,
                "total_units": total
            })

        return result