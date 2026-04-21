import pygame
import math
import datetime
import os


class MickeyClock:
    FACE_RADIUS = 230
    CENTER = (300, 300)
    MIN_LENGTH = 170
    SEC_LENGTH = 145
    BG_COLOR = (245, 245, 245)
    FACE_COLOR = (255, 248, 220)
    FACE_BORDER = (40, 40, 40)
    TICK_COLOR = (80, 80, 80)

    def __init__(self):
        self.hand_img_right = None
        self.hand_img_left = None
        self._load_images()
        pygame.font.init()
        self.font_time = pygame.font.SysFont("Consolas", 44, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 18)
        self.font_tick = pygame.font.SysFont("Arial", 20, bold=True)

    def _load_images(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "mickey_hand.png")
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (60, 100))
            self.hand_img_right = img
            self.hand_img_left = pygame.transform.flip(img, True, False)

    @staticmethod
    def _angle_to_vec(angle_deg, length):
        rad = math.radians(angle_deg)
        return math.sin(rad) * length, -math.cos(rad) * length

    def _draw_image_hand(self, surface, img, angle_deg, length):
        rotated = pygame.transform.rotate(img, -angle_deg)
        cx, cy = self.CENTER
        dx, dy = self._angle_to_vec(angle_deg, length)
        rect = rotated.get_rect(center=(int(cx + dx), int(cy + dy)))
        surface.blit(rotated, rect)

    def _draw_face(self, surface):
        cx, cy = self.CENTER
        r = self.FACE_RADIUS

        shadow_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 40), (r + 10, r + 10), r + 8)
        surface.blit(shadow_surf, (cx - r - 10, cy - r - 10))

        pygame.draw.circle(surface, self.FACE_COLOR, (cx, cy), r)
        pygame.draw.circle(surface, self.FACE_BORDER, (cx, cy), r, 4)

        for i in range(60):
            angle = math.radians(i * 6)
            if i % 5 == 0:
                r1, r2, w = r - 22, r - 6, 3
            else:
                r1, r2, w = r - 10, r - 4, 1
            x1 = cx + r1 * math.sin(angle)
            y1 = cy - r1 * math.cos(angle)
            x2 = cx + r2 * math.sin(angle)
            y2 = cy - r2 * math.cos(angle)
            pygame.draw.line(surface, self.TICK_COLOR, (int(x1), int(y1)), (int(x2), int(y2)), w)

        for h in (12, 3, 6, 9):
            angle = math.radians((h % 12) * 30)
            tx = cx + (r - 46) * math.sin(angle)
            ty = cy - (r - 46) * math.cos(angle)
            label = self.font_tick.render(str(h), True, self.FACE_BORDER)
            surface.blit(label, label.get_rect(center=(int(tx), int(ty))))

    def draw(self, surface):
        surface.fill(self.BG_COLOR)
        self._draw_face(surface)

        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second
        sec_angle = seconds * 6 + now.microsecond / 1_000_000 * 6
        min_angle = minutes * 6 + seconds / 60 * 6

        cx, cy = self.CENTER

        if self.hand_img_right:
            self._draw_image_hand(surface, self.hand_img_left, sec_angle, self.SEC_LENGTH)
            self._draw_image_hand(surface, self.hand_img_right, min_angle, self.MIN_LENGTH)

        pygame.draw.circle(surface, (60, 60, 60), (cx, cy), 12)
        pygame.draw.circle(surface, (220, 220, 220), (cx, cy), 7)

        time_str = f"{minutes:02d}:{seconds:02d}"
        txt = self.font_time.render(time_str, True, (40, 40, 40))
        surface.blit(txt, txt.get_rect(center=(cx, cy + 165)))

        r_label = self.font_label.render("Right hand = Minutes", True, (80, 80, 160))
        l_label = self.font_label.render("Left hand  = Seconds", True, (160, 80, 80))
        surface.blit(r_label, r_label.get_rect(center=(cx, cy + 205)))
        surface.blit(l_label, l_label.get_rect(center=(cx, cy + 228)))
