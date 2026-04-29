import pygame
import sys
from racer import RacerGame
from ui import main_menu, settings_menu, leaderboard_menu, username_input
from persistence import load_settings

pygame.init()
screen = pygame.display.set_mode((400, 700))
pygame.display.set_caption("Racer TSIS 3")
clock = pygame.time.Clock()

def main():
    settings = load_settings()

    while True:
        action = main_menu(screen)

        if action == "play":
            username = username_input(screen)
            game = RacerGame(screen, username, settings)
            game.run()

        elif action == "leaderboard":
            leaderboard_menu(screen)

        elif action == "settings":
            settings = settings_menu(screen, settings)

        elif action == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()