import curses
from time import sleep

#Valeur à mofifier selon si on veut plus ou moins de place pour afficher les infos de jeu
CONST_W = 0

class Terminal :
    def __init__(self, battle):
        self.stdscr = None
        self.runing = True
        self.battle = battle
        self.map = battle.world_map #recupere la map

        #Camera
        self.cam_x, self.cam_y = 0,0

        #taille d'affichage de map dans le terminal
        self.view_h=0
        self.view_w=0     

    # =============================
    # POINT D’ENTRÉE PUBLIC
    # =============================
    def run(self):
        curses.wrapper(self._main) 

    # =============================
    # MAIN INTERNE (Ne pas utiliser)
    # =============================
    def _main(self, stdsrc):
        self.stdscr = stdsrc

        self._init_curses()
        self._init_screen()

        while self.runing :
            self._update()
            self._draw_terminal()
            sleep(0.02)      # ~50 FPS/20ms

    def _init_curses(self):
        self.stdscr.keypad(True)    #Actctivation de la lecture du clavier
        self.stdscr.nodelay(True)   #Mode non bloquant si getch() n'a pas recu de valeur
        curses.curs_set(0)

    def _init_screen(self):
        height, width = self.stdscr.getmaxyx()   #taille du terminal
        info_h = len(self._info_lines())     #Calcul de la taille de la barre d'info
        self.view_h = max(0, height - info_h)    #Permet de connaitre la taille de la map
        self.view_w = width - CONST_W

    # =============================
    # BOUCLE DE JEU
    # =============================
    def _update(self):
        key=self.stdscr.getch()
        self._keyboard_input(key)
        self._limit_camera()
    
    def _draw_terminal(self):
        self.stdscr.clear()
        self._draw_info(self.view_h)
        self._draw_map()
        self.stdscr.refresh()

    # =============================
    # INPUT
    # =============================
    def _keyboard_input(self, key):
        #Arret d'affichage
        if key == ord('q'):
            self.runing = False

        #Déplacer la caméra
        if key==curses.KEY_UP:
            self.cam_y-=1
        elif key==curses.KEY_DOWN:
            self.cam_y+=1
        elif key==curses.KEY_LEFT:
            self.cam_x-=1 
        elif key==curses.KEY_RIGHT:
            self.cam_x+=1

    # =============================
    # LIMITE LA CAMERA
    # =============================
    def _limit_camera(self):
        self.cam_x = max(0, min(self.cam_x, self.map.get_width() - self.view_w))
        self.cam_y = max(0, min(self.cam_y, self.map.get_height() - self.view_h))

    # =============================
    # DESSIN
    # =============================
    def _draw_info(self, start_y):
        for i, line in enumerate(self._info_lines()):
            self.stdscr.addstr(start_y + i, 0, line)

    
    def _draw_map(self):
        units = self.battle.all_units()
        units_by_cell = {}

        for u in units:
            x = int(u.x)
            y = int(u.y)
            units_by_cell[(x, y)] = u

        for y in range(self.view_h):
            for x in range(self.view_w):
                #cam_x cam_y montre dans quelle partie de la map (carte pour éviter ambiguité) on est, x et y montre à quel endroit sur cette "page" on est.
                carte_y = self.cam_y + y
                carte_x = self.cam_x + x

                #si la ligne ou la colonne demandé n'existe pas
                if carte_y >= self.map.get_height() or carte_x >= self.map.get_width():
                    continue

                if (carte_x, carte_y) in units_by_cell:
                    char = units_by_cell[(carte_x, carte_y)].get_symbol()
                else:
                    char = "."

                self.stdscr.addstr(y, x, char) #il faut récupérer ce que je dois marquer

    # =============================
    # TAILLE MAP = f(TAILLE INFO)
    # =============================
    def _info_lines(self):
        return [
            "Q : Quitter"
        ]


"""
Terminal
│
├── run()
├── _main()
│    ├── _update()
│    └── _draw terminal()
│          ├── _draw_info()
│          └── _draw_map()
"""
