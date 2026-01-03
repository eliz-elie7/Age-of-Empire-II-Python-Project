import curses


def afficher_grille(stdscr, grille, curseur_y, curseur_x):
    """Affiche la grille avec le curseur"""
    stdscr.clear()

    # Parcourir chaque ligne de la grille
    for y, ligne in enumerate(grille):
        # Parcourir chaque colonne de la ligne
        for x, valeur in enumerate(ligne):
            # Définir le caractère à afficher
            if valeur == 0:
                char = "□"  # Case vide
            else:
                char = "■"  # Case pleine

            # Mettre en surbrillance la case sous le curseur
            if y == curseur_y and x == curseur_x:
                stdscr.addstr(y, x * 2, char, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x * 2, char)

    # Instructions
    stdscr.addstr(len(grille) + 1, 0, "Flèches: déplacer | Espace: inverser | Q: quitter")
    stdscr.refresh()


def main(stdscr):
    # Initialisation de curses
    curses.curs_set(0)  # Masquer le curseur terminal

    # Création de la grille (10x10 initialement vide)
    hauteur, largeur = 100, 100
    grille = [[0 for _ in range(largeur)] for _ in range(hauteur)]

    # Position du curseur
    curseur_y, curseur_x = 0, 0

    while True:
        afficher_grille(stdscr, grille, curseur_y, curseur_x)

        # Attendre une touche
        key = stdscr.getch()

        # Navigation avec les flèches
        if key == curses.KEY_UP and curseur_y > 0:
            curseur_y -= 1
        elif key == curses.KEY_DOWN and curseur_y < hauteur - 1:
            curseur_y += 1
        elif key == curses.KEY_LEFT and curseur_x > 0:
            curseur_x -= 1
        elif key == curses.KEY_RIGHT and curseur_x < largeur - 1:
            curseur_x += 1

        # Espace pour inverser la valeur de la case
        elif key == ord(' '):
            grille[curseur_y][curseur_x] = 1 - grille[curseur_y][curseur_x]

        # Q pour quitter
        elif key == ord('q') or key == ord('Q'):
            break


# Lancer l'application
if __name__ == "__main__":
    curses.wrapper(main)

#argument 