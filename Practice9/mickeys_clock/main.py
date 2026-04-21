import sys
import pygame
from clock import MickeyClock


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Mickey's Clock")

    clock_widget = MickeyClock()
    fps_clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        clock_widget.draw(screen)
        pygame.display.flip()
        fps_clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
