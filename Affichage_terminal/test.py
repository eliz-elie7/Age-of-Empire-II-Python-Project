import curses
from time import sleep

#y c'est les ligne (height) et x c'est les colonnes

#Partie de Simon: à enlever
class Map:
    def __init__(self, width, height):
        self.width=width #x
        self.height=height #y
        self.data = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    row.append("#")
                else:
                    row.append(".")
            self.data.append(row)
        

    #----- Dimensions -----
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height



"""création fonction (il va fallloir la convertir en methode)
    qui va dessiner la grille uniquement sur la partie visible du terminal"""
#réutilisable pour ecrire les infos du menu
def draw_map(stdscr, map, cam_x, cam_y, view_h, view_w): #h et l a recuperer de map
    for y in range(view_h):
        for x in range(view_w):
            #cam_x cam_y montre dans quelle partie de la map (carte pour éviter ambiguité) on est, x et y montre à quel endroit sur cette "page" on est.
            carte_y = cam_y + y
            carte_x = cam_x + x

            #si la ligne ou la colonne demandé n'existe pas
            if carte_y >= map.get_height() or carte_x >= map.get_width():
                continue

            stdscr.addstr(y, x, map.data[carte_y][carte_x]) #il faut récupérer ce que je dois marquer
    stdscr.refresh()

def move_camera(cam_x, cam_y, key, map1, view_w, view_h):
    if key==curses.KEY_UP:
        cam_y-=1
    elif key==curses.KEY_DOWN:
        cam_y+=1
    elif key==curses.KEY_LEFT:
        cam_x-=1 
    elif key==curses.KEY_RIGHT:
        cam_x+=1   
    else:
        pass
    
    #Limite de map
    cam_x = max(0, min(cam_x, map1.width - view_w))
    cam_y = max(0, min(cam_y, map1.height - view_h))

    return cam_x, cam_y #renvoi un tuple de valeur

def quit(key):
    return key==ord('q')



def main(stdscr):
    #map : à récupérer de chez Simon
    map1=Map(100,100)
    h=10 #hauteur y de map
    l=100  #largeur x de map
    #On récupère la taille du terminal
    height, width = stdscr.getmaxyx()
    #création d'une marque pour mettre des infos de jeu (barre d'info...)
    view_h=height-5
    view_w=width-0
    #Actctivation de la lecture du clavier
    stdscr.keypad(True)
    #Mode non bloquant(si getch n'a pas recu de valeur, on passe a la suite)
    stdscr.nodelay(True)

    #création de la caméra qui nous donne des info sur quelle partie de la map on a bsoin d'écirire sur le terminal
    #elle est en un point => on affiche x,y sur la page de la caméra
    cam_x, cam_y = 0,0

    draw_map(stdscr,map1, cam_x, cam_y, view_h, view_w)

    while(True):
        key=stdscr.getch() #lecture de la touche tapée
        cam_x, cam_y = move_camera(cam_x, cam_y, key, map1, view_w, view_h)
        draw_map(stdscr, map1, cam_x, cam_y, view_h, view_w)
        if quit(key):
            break
            


 
    sleep(1)

#si taille>height ou width on affiche que la première partir de la grille 
# de taille height*taille ou taille*width ou height*width 
# en commencant par le début et on va jouer avec le cureseur pour que 
# la map se déplace   

# Lancer l'application
if __name__ == "__main__":
    #code wrapper stdscr = curses.initscr() initilise stdrc avant de lancer main
    curses.wrapper(main)


#1er test curses : affichage/couleur/texte
"""curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.addstr(0,0,"Bonjour")
    stdscr.addstr("Pretty text", curses.color_pair(1))
    stdscr.refresh()
    stdscr.addstr(10,0,"Hello")
    stdscr.addstr(1,0,"Au revoir")
    stdscr.addstr(0,1,"good bye")
    stdscr.refresh()
    sleep(5)
    stdscr.addstr(1,0,"Salut")
    stdscr.addstr("Pretty texte", curses.color_pair(2))"""

#1er test de mapping
"""
    #taille = donnée de la map a récupérer 
    taille = 100
    for i in range(taille):
        for j in range(taille):
            if i%2==0:
                if j%2==0 :
                    stdscr.addstr(i,j,"+")
                else :
                    stdscr.addstr(i,j, "-")
            else:
                if j%2==1 :
                    stdscr.addstr(i,j,"+")
                else :
                    stdscr.addstr(i,j, "-")
    stdscr.refresh()"""


