# main.py
# Lance une bataille et gère F11 / F12 pour sauvegarde et chargement

import pygame
from battle import Battle
from game_state import GameState
from save_system import save_game, load_game


# l'initialisation pygame


pygame.init()
screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Battle Engine — Save / Load")

clock = pygame.time.Clock()
#La boucle principale

running = True

while running:
    for event in pygame.event.get():
        # Quitter
        if event.type == pygame.QUIT:
            running = False

        # Touches clavier
        if event.type == pygame.KEYDOWN:

            # F11 = Sauvegarder
            if event.key == pygame.K_F11:
                save_game(game_state)

            # F12 = Charger
            if event.key == pygame.K_F12:
                loaded = load_game()
                if loaded:
                    game_state = loaded
                    print("[INFO] Bataille restaurée :", game_state)


    # Update
    if not game_state.finished:
        game_state.update()


    #Affichage

    screen.fill((20, 20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
