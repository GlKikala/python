import pygame

pygame.font.init()

FONT = pygame.font.SysFont("Arial", 26)
BIG_FONT = pygame.font.SysFont("Arial", 48)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
BLUE = (50, 130, 230)
GREEN = (40, 180, 80)
RED = (220, 60, 60)
YELLOW = (230, 210, 50)


class Button:
    """Simple button made only with pygame."""
    def __init__(self, text, rect, color=BLUE):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            color = (
                min(self.color[0] + 25, 255),
                min(self.color[1] + 25, 255),
                min(self.color[2] + 25, 255)
            )
        else:
            color = self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_text(screen, text, x, y, color=BLACK, font=FONT, center=False):
    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
        screen.blit(surface, rect)
    else:
        screen.blit(surface, (x, y))


def get_username(screen, clock, width, height):
    """Username entry screen using pygame keyboard typing."""
    username = ""

    while True:
        screen.fill((235, 235, 235))

        draw_text(screen, "Enter username", width // 2, 180, BLACK, BIG_FONT, center=True)
        draw_text(screen, username + "|", width // 2, 280, BLACK, FONT, center=True)
        draw_text(screen, "ENTER = continue, ESC = back", width // 2, 340, DARK_GRAY, SMALL_FONT, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username.strip():
                        return username.strip()
                    return "Player"

                elif event.key == pygame.K_ESCAPE:
                    return None

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode

        pygame.display.flip()
        clock.tick(60)