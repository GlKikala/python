import pygame
import sys
from persistence import load_leaderboard, save_settings

pygame.init()
FONT = pygame.font.SysFont("Arial", 28)
SMALL = pygame.font.SysFont("Arial", 22)

def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def button(screen, text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (100, 100, 100), rect)
    draw_text(screen, text, SMALL, (255,255,255), x+20, y+10)
    return rect

def main_menu(screen):
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "RACER GAME", FONT, (255,255,255), 110, 100)

        play = button(screen, "Play", 120, 200, 160, 50)
        lb = button(screen, "Leaderboard", 120, 280, 160, 50)
        settings = button(screen, "Settings", 120, 360, 160, 50)
        quitb = button(screen, "Quit", 120, 440, 160, 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play.collidepoint(event.pos): return "play"
                if lb.collidepoint(event.pos): return "leaderboard"
                if settings.collidepoint(event.pos): return "settings"
                if quitb.collidepoint(event.pos): return "quit"

def username_input(screen):
    name = ""
    while True:
        screen.fill((20,20,20))
        draw_text(screen, "Enter Username:", FONT, (255,255,255), 90, 200)
        draw_text(screen, name, FONT, (0,255,0), 130, 300)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:
                        name += event.unicode

def settings_menu(screen, settings):
    options = ["sound", "car_color", "difficulty"]
    idx = 0
    values = {
        "sound": [True, False],
        "car_color": ["red", "blue", "green"],
        "difficulty": ["easy", "normal", "hard"]
    }

    while True:
        screen.fill((40,40,40))
        draw_text(screen, "SETTINGS", FONT, (255,255,255), 120, 80)

        y = 180
        for i, key in enumerate(options):
            color = (255,255,0) if i == idx else (255,255,255)
            draw_text(screen, f"{key}: {settings[key]}", SMALL, color, 80, y)
            y += 80

        draw_text(screen, "ENTER = save", SMALL, (200,200,200), 100, 500)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(options)
                elif event.key == pygame.K_RIGHT:
                    key = options[idx]
                    vals = values[key]
                    pos = vals.index(settings[key])
                    settings[key] = vals[(pos+1) % len(vals)]
                elif event.key == pygame.K_RETURN:
                    save_settings(settings)
                    return settings

def leaderboard_menu(screen):
    data = load_leaderboard()

    while True:
        screen.fill((15,15,15))
        draw_text(screen, "TOP 10", FONT, (255,255,255), 140, 50)

        y = 120
        for i, row in enumerate(data[:10]):
            draw_text(screen, f"{i+1}. {row['name']}  {row['score']}  {row['distance']}m", SMALL, (255,255,255), 40, y)
            y += 45

        back = button(screen, "Back", 130, 620, 140, 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos):
                    return