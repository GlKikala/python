import pygame

from db import create_tables, save_result, get_personal_best, get_top_scores
from settings_manager import load_settings, save_settings
from game import SnakeGame, WIDTH, HEIGHT
from ui import Button, draw_text, get_username, BIG_FONT, FONT
from ui import BLACK, BLUE, GREEN, RED, YELLOW


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake Game")
clock = pygame.time.Clock()


def main_menu():
    buttons = {
        "play": Button("Play", (250, 220, 200, 55), GREEN),
        "leaderboard": Button("Leaderboard", (250, 295, 200, 55), BLUE),
        "settings": Button("Settings", (250, 370, 200, 55), BLUE),
        "quit": Button("Quit", (250, 445, 200, 55), RED),
    }

    while True:
        screen.fill((235, 235, 235))

        draw_text(screen, "TSIS4 Snake", WIDTH // 2, 90, BLACK, BIG_FONT, center=True)
        draw_text(screen, "Database Integration & Advanced Gameplay", WIDTH // 2, 155, BLACK, FONT, center=True)

        for button in buttons.values():
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            for action, button in buttons.items():
                if button.is_clicked(event):
                    return action

        pygame.display.flip()
        clock.tick(60)


def leaderboard_screen():
    back_button = Button("Back", (250, 630, 200, 50), RED)

    while True:
        screen.fill((245, 245, 245))

        draw_text(screen, "Leaderboard Top 10", WIDTH // 2, 70, BLACK, BIG_FONT, center=True)

        draw_text(screen, "Rank", 40, 130)
        draw_text(screen, "Username", 120, 130)
        draw_text(screen, "Score", 300, 130)
        draw_text(screen, "Level", 410, 130)
        draw_text(screen, "Date", 500, 130)

        try:
            rows = get_top_scores()
        except Exception as error:
            rows = []
            draw_text(screen, "Database error. Check config.py and PostgreSQL.", WIDTH // 2, 230, RED, FONT, center=True)
            draw_text(screen, str(error)[:60], WIDTH // 2, 270, RED, FONT, center=True)

        y = 175

        if not rows:
            draw_text(screen, "No scores yet", WIDTH // 2, 260, BLACK, FONT, center=True)

        for i, row in enumerate(rows, start=1):
            username, score, level, date = row

            draw_text(screen, i, 55, y)
            draw_text(screen, username, 120, y)
            draw_text(screen, score, 310, y)
            draw_text(screen, level, 425, y)
            draw_text(screen, date, 500, y, font=FONT)

            y += 42

        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if back_button.is_clicked(event):
                return "menu"

        pygame.display.flip()
        clock.tick(60)


def settings_screen(settings):
    grid_button = Button("", (210, 200, 280, 50), BLUE)
    sound_button = Button("", (210, 280, 280, 50), BLUE)
    color_button = Button("", (210, 360, 280, 50), BLUE)
    save_button = Button("Save & Back", (250, 500, 200, 55), GREEN)

    colors = [
        [0, 200, 0],
        [0, 120, 255],
        [220, 50, 50],
        [180, 0, 220],
        [255, 180, 0]
    ]

    while True:
        screen.fill((235, 235, 235))

        draw_text(screen, "Settings", WIDTH // 2, 90, BLACK, BIG_FONT, center=True)

        grid_button.text = f"Grid: {'ON' if settings['grid'] else 'OFF'}"
        sound_button.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color_button.text = f"Snake color: {settings['snake_color']}"

        grid_button.draw(screen)
        sound_button.draw(screen)
        color_button.draw(screen)
        save_button.draw(screen)

        preview_rect = pygame.Rect(320, 440, 60, 35)
        pygame.draw.rect(screen, tuple(settings["snake_color"]), preview_rect)
        pygame.draw.rect(screen, BLACK, preview_rect, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if grid_button.is_clicked(event):
                settings["grid"] = not settings["grid"]

            elif sound_button.is_clicked(event):
                settings["sound"] = not settings["sound"]

            elif color_button.is_clicked(event):
                index = colors.index(settings["snake_color"]) if settings["snake_color"] in colors else 0
                settings["snake_color"] = colors[(index + 1) % len(colors)]

            elif save_button.is_clicked(event):
                save_settings(settings)
                return "menu"

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(username, score, level):
    retry_button = Button("Retry", (250, 430, 200, 55), GREEN)
    menu_button = Button("Main Menu", (250, 510, 200, 55), BLUE)

    try:
        best = get_personal_best(username)
    except Exception:
        best = score

    while True:
        screen.fill((235, 235, 235))

        draw_text(screen, "Game Over", WIDTH // 2, 120, BLACK, BIG_FONT, center=True)

        draw_text(screen, f"Player: {username}", WIDTH // 2, 215, BLACK, FONT, center=True)
        draw_text(screen, f"Final score: {score}", WIDTH // 2, 260, BLACK, FONT, center=True)
        draw_text(screen, f"Level reached: {level}", WIDTH // 2, 305, BLACK, FONT, center=True)
        draw_text(screen, f"Personal best: {best}", WIDTH // 2, 350, BLACK, FONT, center=True)

        retry_button.draw(screen)
        menu_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if retry_button.is_clicked(event):
                return "retry"

            if menu_button.is_clicked(event):
                return "menu"

        pygame.display.flip()
        clock.tick(60)


def play_game(settings):
    username = get_username(screen, clock, WIDTH, HEIGHT)

    if username is None:
        return "menu"

    while True:
        game = SnakeGame(screen, clock, username, settings)
        status, score, level = game.run()

        if status == "quit":
            return "quit"

        try:
            save_result(username, score, level)
        except Exception as error:
            print("Could not save result:", error)

        action = game_over_screen(username, score, level)

        if action == "retry":
            continue

        return action


def main():
    try:
        create_tables()
    except Exception as error:
        print("Database connection error:", error)

    settings = load_settings()

    while True:
        action = main_menu()

        if action == "quit":
            break

        elif action == "play":
            result = play_game(settings)
            if result == "quit":
                break

        elif action == "leaderboard":
            result = leaderboard_screen()
            if result == "quit":
                break

        elif action == "settings":
            result = settings_screen(settings)
            if result == "quit":
                break

    pygame.quit()


if __name__ == "__main__":
    main()