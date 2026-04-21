import sys
import pygame
from ball import Ball

W, H = 800, 600
BG = (255, 255, 255)
GRID = (235, 235, 235)


def draw_grid(surface):
    for x in range(0, W, 40):
        pygame.draw.line(surface, GRID, (x, 0), (x, H))
    for y in range(0, H, 40):
        pygame.draw.line(surface, GRID, (0, y), (W, y))


def draw_hud(surface, font, ball, ignored):
    pos_txt = font.render(f"Position:  x={ball.x}  y={ball.y}", True, (60, 60, 60))
    surface.blit(pos_txt, (10, 10))

    hint = font.render("Arrow keys = move   |   ESC = quit", True, (160, 160, 160))
    surface.blit(hint, (10, H - 28))

    if ignored:
        warn = font.render("Boundary reached — move ignored", True, (200, 80, 80))
        surface.blit(warn, (W - warn.get_width() - 10, 10))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Moving Ball")

    ball = Ball(W, H)
    font = pygame.font.SysFont("Consolas", 16)
    clock = pygame.time.Clock()
    ignored = False
    ignored_timer = 0

    running = True
    while running:
        dt = clock.tick(60)

        if ignored_timer > 0:
            ignored_timer -= dt
            if ignored_timer <= 0:
                ignored = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                moved = False
                if event.key == pygame.K_UP:
                    moved = ball.move_up()
                elif event.key == pygame.K_DOWN:
                    moved = ball.move_down()
                elif event.key == pygame.K_LEFT:
                    moved = ball.move_left()
                elif event.key == pygame.K_RIGHT:
                    moved = ball.move_right()
                else:
                    continue
                if not moved:
                    ignored = True
                    ignored_timer = 800

        screen.fill(BG)
        draw_grid(screen)
        ball.draw(screen)
        draw_hud(screen, font, ball, ignored)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
