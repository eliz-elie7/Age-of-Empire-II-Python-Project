import curses
from time import sleep

#y c'est les ligne et x c'est les colonnes

"""création fonction (il va fallloir la convertir en methode)
    qui va dessiner la grille uniquement sur la partie visible du terminal"""
#réutilisable pour ecrire les infos du menu
def draw_map(stdscr, h, l, cam_x, cam_y, view_h, view_w): #h et l a recuperer de map
    for y in range(view_h):
        for x in range(view_w):
            #cam_x cam_y montre dans quelle partie de la map on est, x et y montre à quel endroit sur cette "page" on est.
            map_y = cam_y + y
            map_x = cam_x + x

            #si la ligne ou la colonne demandé n'existe pas
            if map_y >= h or map_x >= l:
                continue

            stdscr.addstr(y, x, ".") #il faut récupérer ce que je dois marquer
    stdscr.refresh()


def main(stdscr):
    #taille= donnée de la map a récupérer 
    taille = 100
    h=10 #hauteur y de map
    l=100  #largeur x de map
    #On récupère la taille du terminal
    height, width = stdscr.getmaxyx()
    #création d'une marque pour mettre des infos de jeu (barre d'info...)
    view_h=height-5
    view_w=width-0
    #création de la caméra qui nous donne des info sur quelle partie de la map on a bsoin d'écirire sur le terminal
    #elle est en un point => on affiche x,y sur la page de la caméra
    cam_x =0 
    cam_y = 0
    draw_map(stdscr, h, l, cam_x, cam_y, view_h, view_w)

    sleep(15)

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
"""for i in range(taille):
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


