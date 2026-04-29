"""
TSIS2 — Paint Application
Tools: Pencil, Straight Line, Flood-Fill, Text
Brush sizes: 1=2px, 2=5px, 3=10px
Ctrl+S — save canvas as timestamped PNG
"""

import pygame
import sys
from datetime import datetime
from tools import flood_fill

pygame.init()

# ── Layout ──────────────────────────────────────────────
W, H = 1000, 700
TB_H = 65          # toolbar height
CANVAS_TOP = TB_H
CANVAS_H = H - TB_H

# ── Colors ──────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
BG          = (210, 210, 210)
ACTIVE_BG   = (120, 120, 120)
BTN_BORDER  = (60,  60,  60)
PALETTE = [
    (0,0,0),(255,255,255),(200,200,200),(100,100,100),
    (255,0,0),(180,0,0),(255,140,0),(255,220,0),
    (0,200,0),(0,100,0),(0,180,255),(0,0,220),
    (180,0,255),(255,100,200),(139,69,19),(255,200,150),
]
BRUSH_SIZES = [2, 5, 10]
TOOLS = ['pencil', 'line', 'fill', 'text']
TOOL_LABELS = ['Pencil(P)', 'Line(L)', 'Fill(F)', 'Text(T)']
TOOL_KEYS   = [pygame.K_p, pygame.K_l, pygame.K_f, pygame.K_t]


class PaintApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Paint — TSIS2")
        self.clock = pygame.time.Clock()

        # canvas as a separate surface
        self.canvas = pygame.Surface((W, CANVAS_H))
        self.canvas.fill(WHITE)

        self.tool = 'pencil'
        self.color = BLACK
        self.size  = BRUSH_SIZES[1]      # default medium

        # drawing state
        self.drawing     = False
        self.last_pos    = None
        self.line_start  = None
        self.canvas_bak  = None          # backup for live line preview

        # text state
        self.text_active = False
        self.text_pos    = None
        self.text_buf    = ''

        self.font_ui   = pygame.font.SysFont('Consolas', 13)
        self.font_text = pygame.font.SysFont('Arial',    22)

        # pre-build toolbar button rects
        self._build_rects()

    # ── Build toolbar layout ─────────────────────────────
    def _build_rects(self):
        self.tool_rects  = []
        self.size_rects  = []
        self.pal_rects   = []

        x = 5
        for i in range(len(TOOLS)):
            self.tool_rects.append(pygame.Rect(x, 5, 72, 26))
            x += 76

        x += 8
        for i in range(3):
            self.size_rects.append(pygame.Rect(x, 5, 40, 26))
            x += 44

        x += 10
        for i in range(len(PALETTE)):
            self.pal_rects.append(pygame.Rect(x, 8, 22, 22))
            x += 26

    # ── Coordinate helpers ───────────────────────────────
    def to_canvas(self, screen_pos):
        return (screen_pos[0], screen_pos[1] - CANVAS_TOP)

    def in_canvas(self, screen_pos):
        return screen_pos[1] >= CANVAS_TOP

    # ── Draw toolbar ─────────────────────────────────────
    def draw_toolbar(self):
        pygame.draw.rect(self.screen, BG, (0, 0, W, TB_H))
        pygame.draw.line(self.screen, BTN_BORDER, (0, TB_H - 1), (W, TB_H - 1))

        # Tool buttons
        for i, (rect, lbl) in enumerate(zip(self.tool_rects, TOOL_LABELS)):
            bg = ACTIVE_BG if TOOLS[i] == self.tool else BG
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, BTN_BORDER, rect, 1)
            t = self.font_ui.render(lbl, True, BLACK)
            self.screen.blit(t, (rect.x + 3, rect.y + 6))

        # Size buttons
        for i, (rect, s) in enumerate(zip(self.size_rects, BRUSH_SIZES)):
            bg = ACTIVE_BG if s == self.size else BG
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, BTN_BORDER, rect, 1)
            t = self.font_ui.render(str(i + 1), True, BLACK)
            self.screen.blit(t, (rect.x + 14, rect.y + 6))

        # Palette swatches
        for i, (rect, c) in enumerate(zip(self.pal_rects, PALETTE)):
            pygame.draw.rect(self.screen, c, rect)
            pygame.draw.rect(self.screen, BTN_BORDER, rect, 1)
            if c == self.color:
                pygame.draw.rect(self.screen, WHITE, rect.inflate(-4, -4), 2)

        # Status bar (bottom of toolbar)
        mode_str = f"  Tool: {self.tool}   Size: {self.size}px   Color: {self.color}   Ctrl+S = Save"
        if self.text_active:
            mode_str += f"   Typing: '{self.text_buf}'  [Enter=confirm  Esc=cancel]"
        st = self.font_ui.render(mode_str, True, (50, 50, 50))
        self.screen.blit(st, (5, 46))

        # Current color preview
        pr = pygame.Rect(W - 55, 5, 50, 55)
        pygame.draw.rect(self.screen, self.color, pr)
        pygame.draw.rect(self.screen, BTN_BORDER, pr, 2)

    # ── Events ───────────────────────────────────────────
    def handle(self, event):
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        # ── Keyboard ─────────────────────────────────────
        if event.type == pygame.KEYDOWN:
            if self.text_active:
                self._text_key(event)
                return
            if event.key == pygame.K_1: self.size = BRUSH_SIZES[0]
            if event.key == pygame.K_2: self.size = BRUSH_SIZES[1]
            if event.key == pygame.K_3: self.size = BRUSH_SIZES[2]
            for k, t in zip(TOOL_KEYS, TOOLS):
                if event.key == k:
                    self.tool = t
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.save()

        # ── Mouse button down ─────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if not self.in_canvas(pos):
                self._toolbar_click(pos)
                return
            cp = self.to_canvas(pos)
            if self.tool == 'pencil':
                self.drawing   = True
                self.last_pos  = cp
            elif self.tool == 'line':
                self.drawing     = True
                self.line_start  = cp
                self.canvas_bak  = self.canvas.copy()
            elif self.tool == 'fill':
                flood_fill(self.canvas, cp, self.color)
            elif self.tool == 'text':
                self.text_active = True
                self.text_pos    = cp
                self.text_buf    = ''

        # ── Mouse motion ──────────────────────────────────
        if event.type == pygame.MOUSEMOTION and self.drawing:
            cp = self.to_canvas(event.pos)
            if self.tool == 'pencil' and self.last_pos:
                pygame.draw.line(self.canvas, self.color,
                                 self.last_pos, cp, self.size)
                self.last_pos = cp
            elif self.tool == 'line' and self.line_start:
                self.canvas.blit(self.canvas_bak, (0, 0))
                pygame.draw.line(self.canvas, self.color,
                                 self.line_start, cp, self.size)

        # ── Mouse button up ───────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drawing:
                cp = self.to_canvas(event.pos)
                if self.tool == 'line' and self.line_start:
                    self.canvas.blit(self.canvas_bak, (0, 0))
                    pygame.draw.line(self.canvas, self.color,
                                     self.line_start, cp, self.size)
                self.drawing    = False
                self.last_pos   = None
                self.line_start = None
                self.canvas_bak = None

    def _text_key(self, event):
        if event.key == pygame.K_RETURN:
            if self.text_buf:
                surf = self.font_text.render(self.text_buf, True, self.color)
                self.canvas.blit(surf, self.text_pos)
            self.text_active = False
            self.text_buf    = ''
        elif event.key == pygame.K_ESCAPE:
            self.text_active = False
            self.text_buf    = ''
        elif event.key == pygame.K_BACKSPACE:
            self.text_buf = self.text_buf[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                self.text_buf += event.unicode

    def _toolbar_click(self, pos):
        for i, rect in enumerate(self.tool_rects):
            if rect.collidepoint(pos):
                self.tool = TOOLS[i]; return
        for i, rect in enumerate(self.size_rects):
            if rect.collidepoint(pos):
                self.size = BRUSH_SIZES[i]; return
        for i, rect in enumerate(self.pal_rects):
            if rect.collidepoint(pos):
                self.color = PALETTE[i]; return

    def save(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = f'canvas_{ts}.png'
        pygame.image.save(self.canvas, name)
        pygame.display.set_caption(f"Paint — saved: {name}")
        print(f"[Paint] Saved → {name}")

    # ── Main loop ─────────────────────────────────────────
    def run(self):
        while True:
            for ev in pygame.event.get():
                self.handle(ev)

            self.screen.blit(self.canvas, (0, CANVAS_TOP))
            self.draw_toolbar()

            # Live text preview
            if self.text_active and self.text_pos:
                preview = self.font_text.render(self.text_buf + '|', True, self.color)
                sp = (self.text_pos[0], self.text_pos[1] + CANVAS_TOP)
                self.screen.blit(preview, sp)

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == '__main__':
    PaintApp().run()
