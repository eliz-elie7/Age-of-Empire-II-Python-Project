import curses
from .view_base import View

#Valeur à mofifier selon si on veut plus ou moins de place pour afficher les infos de jeu
CONST_W = 0

TILE = 32

class TerminalView(View) :
    def __init__(self):
        super().__init__()
        self.stdscr = None
    
        #Camera (coo haut gauche de la vue)
        self.cam_x, self.cam_y = 0,0

        #taille d'affichage de map dans le terminal
        self.view_h=0
        self.view_w=0  

        #limites de map
        self.map_width = 0
        self.map_height = 0   

    # =============================
    # Def methodes View
    # =============================
    def on_enter(self, battle, game_state): # nouveau main
        self.running = True
        self._switch_requested = False
        self.battle = battle
        self.map_width = battle.world_map.get_width()
        self.map_height = battle.world_map.get_height()

        self.stdscr = curses.initscr()
        self._init_curses()

        self._init_screen(game_state)
        self.center_cam(game_state)
        
    def render(self, game_state): #draw terminal
        self.stdscr.erase()
        self._draw_map(game_state)
        self._draw_info(self.view_h, game_state)
        self.stdscr.refresh()

    def handle_input(self):
        key = self.stdscr.getch()

        if key == -1:
            return None

        #Arret d'affichage
        if key == ord('t') or key == ord('t'):
            self.stop()
            return "quit"

        # Demande de changement de vue
        if key == curses.KEY_F9:
            return "switch_view"

        #Déplacer la caméra
        if key==curses.KEY_UP or key == ord('z'):
            self.cam_y-= TILE
        elif key==curses.KEY_DOWN or key == ord('s'):
            self.cam_y+= TILE
        elif key==curses.KEY_LEFT or key == ord('q'):
            self.cam_x-= TILE
        elif key==curses.KEY_RIGHT or key == ord('d'):
            self.cam_x+= TILE

        if key == ord('Z'):
            self.cam_y-= TILE*10
        elif key == ord('S'):
            self.cam_y+= TILE*10
        elif key == ord('Q'):
            self.cam_x-= TILE*10
        elif key == ord('D'):
            self.cam_x+= TILE*10

        if key== ord('p') or key == ord('P'):
            return "pause"  

        if key == 9 or key == ord('\t'):
            return "\t"
        
        if key == curses.KEY_F11:
            return "save"
        
        if key == curses.KEY_F12:
            return "load"
        
        if key== ord('k') or key == ord('K'):
            return "accelerer"

        """#Recentrer caméra
        if key== ord('c'):
            self.center_camera(game_state)"""

        self._limit_camera() #fonctionde sécurité
        return None

    def on_exit(self):
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    # =============================
    # LOGIQUE INTERNE (Ne pas utiliser)
    # =============================
    def _init_curses(self):
        curses.noecho()   
        curses.cbreak()
        self.stdscr.keypad(True)    #Actctivation de la lecture du clavier
        self.stdscr.nodelay(True)   #Mode non bloquant si getch() n'a pas recu de valeur
        try:
            curses.curs_set(0)      # Cache le curseur
        except curses.error:
            pass

        curses.start_color()
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)      # Paire 2: rouge sur noir
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Paire 1: bleu sur noir
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Paire 3: vert sur noir
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Paire 4: jaune sur noir
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Paire 5: cyan sur noir

    def _init_screen(self, game_state):
        height, width = self.stdscr.getmaxyx()   #taille du terminal
        info_h = len(self._info_lines(game_state))         #Calcul de la taille de la barre d'info
        self.view_h = max(0, height - info_h - 1)    #Permet de connaitre la taille de la map
        self.view_w = width - CONST_W

    # =============================
    # CAMERA
    # =============================
    def center_cam(self, game_state):
        all_x = []
        all_y = []
        for p in game_state["players"]:
            for u in p["units"]:
                all_x.append(u["x"])
                all_y.append(u["y"])

        if not all_x:
            return

        avg_x = sum(all_x) / len(all_x)
        avg_y = sum(all_y) / len(all_y)

        #Centrer (/!\on est en pixel =>(* 32))
        view_w_px = (self.view_w * TILE)/2
        view_h_px = (self.view_h * TILE)/2

        self.cam_x = int(avg_x - (view_w_px / 2))
        self.cam_y = int(avg_y - (view_h_px / 2))

        self._limit_camera()


    def _limit_camera(self):
        max_x = self.map_width - (self.view_w * TILE)
        max_y = self.map_height - (self.view_h * TILE)

        self.cam_x = max(0, min(self.cam_x, self.map_width - self.view_w))
        self.cam_y = max(0, min(self.cam_y, self.map_height - self.view_h))

    # =============================
    # DESSIN
    # =============================
    def _draw_info(self, start_y, game_state):

        lines = self._info_lines(game_state)
        color = curses.color_pair(0)

        for i, line in enumerate(lines):
            if "Army A" in line or "Joueur 1" in line:
                color = curses.color_pair(1) # Bleu
            
            elif "Army B" in line or "Joueur 2" in line:
                color = curses.color_pair(2) # Rouge
            
            elif "---" in line:
                color = curses.color_pair(4)
        
            try:
                self.stdscr.addstr(start_y + i, 0, line[:self.view_w], color)
            except curses.error:
                pass

    
    def _draw_map(self, game_state):                    #tel quel
        units_by_cell = {}
        for i, p in enumerate(game_state["players"]): #recup unit
            color_id=i+1
            for u in p["units"]:
                x = int(u["x"]) //TILE  #les coordonné des unité sont en case et non en pixel
                y = int(u["y"]) //TILE
                units_by_cell[(x, y)] = (u, color_id)

        for y in range(self.view_h):
            for x in range(self.view_w):
                #cam_x cam_y montre dans quelle partie de la map (carte pour éviter ambiguité) on est, x et y montre à quel endroit sur cette "page" on est.
                tile_x = (self.cam_x // TILE) + x
                tile_y = (self.cam_y // TILE) + y

                #si la ligne ou la colonne demandé n'existe pas
                if tile_y >= self.map_height //TILE or tile_x >= self.map_width //TILE:
                    continue

                if (tile_x, tile_y) in units_by_cell:
                    unit_data, col_id = units_by_cell[(tile_x, tile_y)]
                    char = unit_data["symbol"]

                    try:
                        self.stdscr.addch(y, x, char, curses.color_pair(col_id))
                    except curses.error: pass
                else:
                    try:
                        self.stdscr.addch(y, x, ".") 
                    except curses.error: pass 

    # =============================
    # TAILLE MAP = f(TAILLE INFO)
    # =============================
    def _info_lines(self, game_state):
        lines = ["--- MEDIEVAIL INFO ---"]
    
        current_time = getattr(self.battle, 'time', 0.0)
        lines.append(f"Time : {current_time:.1f}s")
        lines.append("-" * 30)

        players = game_state.get('players', [])

        # Trad des symboles en noms
        mapping = {'K': 'Knights', 'P': 'Pikemen', 'A': 'Archers', 'S': 'Soldiers'}
        for i, player in enumerate(players):
            total_alive = 0
            stats_types = {}
            
            units = player.get('units', [])
            army_name = player.get('name', f"Player {i+1}")

            for u in units:
                if u.get('hp', 0) > 0 and u.get('state') != "dead":
                    total_alive += 1
                    sym = u.get('symbol', '?')
                    name = mapping.get(sym, sym) 
                    stats_types[name] = stats_types.get(name, 0) + 1

            # AFFICHAGE
            lines.append(f"{army_name} : {total_alive} alive")
        
            # Utilisation des résultats du mapping
            detail_str = "   |_ "
            # Ici, 's' est déjà le nom complet car on l'a mappé au-dessus
            details = [f"{s}: {n}" for s, n in stats_types.items()]
        
            if details:
                lines.append(detail_str + " | ".join(details))
            else:
                lines.append("   |_ (Plus aucune unité active)")
        

        lines.append("---COMMANDS---")
        lines.append("[T] Quit | [ZQSD]/Arrow Cam | [P] Pause/Play | [Tab] HTML Doc")
        lines.append("[F11/F12] : Save/load | [F9] : 2.5D")
        lines.append(f"CAM: ({self.cam_x//TILE},{self.cam_y//TILE})")

        return lines