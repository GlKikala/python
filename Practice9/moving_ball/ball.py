import pygame


class Ball:
    RADIUS = 25
    STEP = 20
    COLOR = (210, 40, 40)
    OUTLINE = (140, 10, 10)
    HIGHLIGHT = (255, 120, 120)

    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        r = self.RADIUS
        if r <= new_x <= self.sw - r and r <= new_y <= self.sh - r:
            self.x, self.y = new_x, new_y
            return True
        return False

    def move_up(self):    return self.move(0, -self.STEP)
    def move_down(self):  return self.move(0,  self.STEP)
    def move_left(self):  return self.move(-self.STEP, 0)
    def move_right(self): return self.move( self.STEP, 0)

    def draw(self, surface):
        cx, cy = self.x, self.y
        r = self.RADIUS

        shadow = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 50), (r + 4, r + 6), r)
        surface.blit(shadow, (cx - r - 4, cy - r - 4))

        pygame.draw.circle(surface, self.COLOR, (cx, cy), r)
        pygame.draw.circle(surface, self.OUTLINE, (cx, cy), r, 2)
        pygame.draw.circle(surface, self.HIGHLIGHT, (cx - r // 3, cy - r // 3), r // 4)
