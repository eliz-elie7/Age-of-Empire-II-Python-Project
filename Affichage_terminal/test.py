import curses
from time import sleep


def main(stdscr):
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
    taille, h = 100
    l=10
    #On récupère la taille du terminal
    height, width = stdscr.getmaxyx()
    if taille > height:
        if taille > width:
        
        else:
            
    else:
        if taille > width :

        else:
            
    

            


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
    stdscr.refresh()
    sleep(5)
#si taille>height ou width on affiche que la première partir de la grille 
# de taille height*taille ou taille*width ou height*width 
# en commencant par le début et on va jouer avec le cureseur pour que 
# la map se déplace   
#

# Lancer l'application
if __name__ == "__main__":
    #code wrapper stdscr = curses.initscr() initilise stdrc avant de lancer main
    curses.wrapper(main)



