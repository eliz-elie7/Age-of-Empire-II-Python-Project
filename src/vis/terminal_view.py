import os
import sys
import termios
import tty
import select
from .view_base import View


"""class TerminalView:
    Affichage propre et stable dans le terminal.

    def __init__(self, fps: int = 25):
        self.fps = fps
        self._running = True

        # Forcer clear chaque frame
        self.last_clear_time = 0
        self.clear_interval = 0.0

        # 1 caractère = TILE pixels (aligné avec units.TILE). Choisi ici en dur pour éviter imports circulaires.
        self.grid_size_factor = 32.0

        self.min_width = 80
        self.min_height = 20

    def is_running(self) -> bool:
        return self._running

    def _clear_screen(self):
        # Forcer l'effacement à chaque appel pour éviter affichages multiples entre clears
        os.system('cls' if os.name == 'nt' else 'clear')
        self.last_clear_time = time.time()

    def draw(self, state: Dict[str, Any], world_map):
        if not self._running:
            return

        self._clear_screen()

        width_map = world_map.get_width()
        height_map = world_map.get_height()

        grid_width = max(self.min_width, math.ceil(width_map / self.grid_size_factor))
        grid_height = max(self.min_height, math.ceil(height_map / self.grid_size_factor))

        # Grille vide
        grid = [['.' for _ in range(grid_width)] for _ in range(grid_height)]

        # ============================
        #   Placement des unités
        # ============================
        for player in state["players"]:
            for unit in player["units"]:
                gx = int(unit["x"] / self.grid_size_factor)
                gy = int(unit["y"] / self.grid_size_factor)

                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    initial = player["name"][0]
                    grid[gy][gx] = f"{initial}:{unit['symbol']}"

        output = []
        output.append("📊 STATS:")

        for player in state["players"]:
            output.append(f"  {player['name']}: {player['alive_units']} unités vivantes")

            for unit in player["units"]:
                output.append(
                    f"    {unit['symbol']} @ ({unit['x']:.1f}, {unit['y']:.1f}) "
                    f"HP:{unit['hp']}  Ordre:{unit['order']}"
                )

        output.append("=" * grid_width)

        for row in grid:
            output.append(" ".join(row))

        output.append("=" * grid_width)

        output.append(f"🕰️ Temps: {state['game_time']:.2f}s / {state['total_time']:.0f}s")

        if state["finished"]:
            output.append(f"🏆 Vainqueur: {state['winner']}")

        print("\n".join(output))"""
# src/view/terminal_view.py

class TerminalView(View):
    """Affichage propre et stable dans le terminal (hérite de View)."""

    def __init__(self, min_width=60, min_height=40, zoom = 16):
        super().__init__()
        self.width = min_width
        self.height = min_height
        self.last_clear_time = 0
        self.clear_interval = 0.0
        self.zoom = zoom
        # rétrocompatibilité : accepte encore draw(state, world_map)
        # on ne stocke pas fps ici (géré par main)
    def clear(self):
        """Efface le terminal proprement."""
        os.system('cls' if os.name == 'nt' else 'clear')
    # -------------------------
    # utilitaire : lecture non bloquante d'une touche
    # -------------------------
    def _get_char_non_blocking(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            # select pour tester si un caractère est prêt
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                ch = sys.stdin.read(1)
                return ch
            return None
        except Exception:
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # -------------------------
    # API View
    # -------------------------
    def on_enter(self, battle, game_state):
        self._switch_requested = False
        self._running = True
        os.system('clear')

    def render(self, game_state):
        """Render terminal : grille ASCII centrée automatiquement + stats.
        Exige game_state comme dict produit par Battle._build_state_snapshot().
        """
        # clear terminal
        self.clear()

        # sécurité : players sous forme de liste de dicts
        players = game_state.get("players", []) if game_state else []

        # Récupérer toutes les unités (plat)
        units_all = []
        for p_idx, p in enumerate(players):
            for u in p.get("units", []):
                units_all.append((p_idx, p.get("name", f"Player{p_idx}"), u))

        # Si pas d'unités, afficher juste les stats
        if not units_all:
            print("Aucune unité à afficher.")
            print("📊 STATS:")
            for p in players:
                print(f"  {p.get('name')}: {p.get('alive_units', 0)} unités vivantes")
            return

        # Calculer bounding box des unités pour centrer la vue
        xs = [u[2]["x"] for u in units_all]
        ys = [u[2]["y"] for u in units_all]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # centre du groupe
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        # world coords de la case (0,0) de la grille (top-left) : centrer la fenêtre
        half_w_world = (self.width - 1) * self.zoom / 2.0
        half_h_world = (self.height - 1) * self.zoom / 2.0
        top_left_x = center_x - half_w_world
        top_left_y = center_y - half_h_world

        # Préparer la grille vide
        grid = [["." for _ in range(self.width)] for _ in range(self.height)]

        # Couleurs ANSI simples
        COLORS = ["\033[91m", "\033[94m", "\033[92m", "\033[93m"]  # rouge / bleu / vert / jaune
        RESET = "\033[0m"

        # Placements : si plusieurs unités sur même case, on montre un chiffre de pile
        cell_counts = {}  # (gx,gy) -> dict{player_idx:count, total:count, symbol:last_symbol}

        for p_idx, pname, u in units_all:
            # lire coords depuis snapshot dict
            x = float(u.get("x", 0.0))
            y = float(u.get("y", 0.0))

            # conversion vers grille en tenant compte du top-left
            gx = int((x - top_left_x) / self.zoom)
            gy = int((y - top_left_y) / self.zoom)

            if 0 <= gx < self.width and 0 <= gy < self.height:
                key = (gx, gy)
                entry = cell_counts.get(key)
                if entry is None:
                    entry = {"total": 0, "by_player": {}, "symbol": u.get("symbol", "?"), "last_player": p_idx}
                    cell_counts[key] = entry
                entry["total"] += 1
                entry["by_player"][p_idx] = entry["by_player"].get(p_idx, 0) + 1
                entry["symbol"] = u.get("symbol", entry["symbol"])
                entry["last_player"] = p_idx

        # Remplir la grille avec le meilleur affichage possible
        for (gx, gy), entry in cell_counts.items():
            total = entry["total"]
            last_player = entry["last_player"]
            symbol = entry["symbol"] if total == 1 else str(total)  # si pile -> montrer le nombre

            # coloriser par joueur (s'il y a plusieurs joueurs, utiliser la dernière unité)
            color = COLORS[last_player % len(COLORS)]
            grid[gy][gx] = f"{color}{symbol}{RESET}"

        # Afficher la grille
        for row in grid:
            print(" ".join(row))

        # Infos sous la grille
        print("\nZoom:", self.zoom)
        print("Commandes : [Q] quitter  •  [F9] changer de vue\n")

        # Affichage des stats (par joueur)
        print("📊 STATS:")
        for p in players:
            name = p.get("name", "Unknown")
            alive = p.get("alive_units", len([u for u in p.get("units", []) if u.get("hp", 0) > 0]))
            print(f"  {name}: {alive} unités vivantes")
            # afficher résumé compact (up to 6 unités)
            units_list = p.get("units", [])
            for u in units_list[:6]:
                print(f"    {u.get('symbol','?')} @ ({u.get('x',0):.1f},{u.get('y',0):.1f}) HP:{u.get('hp',0):.0f} State:{u.get('state')}")

        # si tu veux debug : afficher bbox et center
        # print(f"\nDBG bbox x:{min_x:.1f}-{max_x:.1f} y:{min_y:.1f}-{max_y:.1f} center:{center_x:.1f},{center_y:.1f}")

    
    def handle_input(self, key=None):
        """Lecture non bloquante si key None. Retourne un event optionnel."""
        if key is None:
            key = self._get_char_non_blocking()

        if key is None:
            return None

        k = key.lower()

        if k == 'q':
            # arrête la vue (main doit détecter et arrêter la boucle si besoin)
            self.stop()
            return "QUIT"

        # Certains terminaux n'envoyent pas F9 comme code simple,
        # on laisse aussi la touche '9' et ESC comme fallback
        if k == '\x1b' or k == '9':
            self.request_switch()
            return "SWITCH"

        # sinon rien
        return None

    def on_exit(self):
        # nettoyage éventuel
        os.system('cls' if os.name == 'nt' else 'clear')

    # -------------------------
    # Rétrocompatibilité avec l'ancien code qui appelait draw(state, world_map)
    # -------------------------
   
