import sys
import os
import pygame
from player import MusicPlayer

W, H = 620, 400
BG = (18, 18, 28)
PANEL = (28, 28, 42)
ACCENT = (100, 180, 255)
WHITE = (240, 240, 240)
GREY = (120, 120, 140)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
BAR_BG = (50, 50, 70)
BAR_FG = (100, 180, 255)


def _fmt_ms(ms):
    if ms < 0:
        return "0:00"
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"


def draw_ui(screen, player, fonts, message):
    screen.fill(BG)

    pygame.draw.rect(screen, PANEL, (0, 0, W, 70))
    title = fonts["big"].render("♪  Music Player", True, ACCENT)
    screen.blit(title, (20, 18))

    pygame.draw.rect(screen, PANEL, (20, 90, W - 40, 100), border_radius=10)

    status_color = GREEN if player.is_playing else RED
    status_txt = "▶  PLAYING" if player.is_playing else "■  STOPPED"
    screen.blit(fonts["med"].render(status_txt, True, status_color), (40, 100))

    if player.playlist:
        idx = player.current_index
        total = player.track_count
        track = fonts["med"].render(f"[{idx + 1}/{total}]  {player.track_name()}", True, WHITE)
        screen.blit(track, (40, 130))
        pos_txt = fonts["small"].render(f"Position: {_fmt_ms(player.position_ms)}", True, GREY)
        screen.blit(pos_txt, (40, 162))
    else:
        screen.blit(fonts["med"].render("No tracks loaded", True, GREY), (40, 130))

    bar_x, bar_y, bar_w, bar_h = 20, 205, W - 40, 14
    pygame.draw.rect(screen, BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=7)
    if player.is_playing and player.position_ms > 0:
        ratio = min(player.position_ms / (5 * 60 * 1000), 1.0)
        pygame.draw.rect(screen, BAR_FG, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=7)

    pygame.draw.rect(screen, PANEL, (20, 232, W - 40, 110), border_radius=10)
    screen.blit(fonts["small"].render("PLAYLIST", True, ACCENT), (36, 240))

    if player.playlist:
        start_idx = max(0, player.current_index - 1)
        for i, path in enumerate(player.playlist[start_idx:start_idx + 4]):
            real_idx = start_idx + i
            color = WHITE if real_idx == player.current_index else GREY
            name = player.track_name(real_idx)
            if len(name) > 55:
                name = name[:52] + "…"
            prefix = "▶ " if real_idx == player.current_index else "  "
            screen.blit(fonts["small"].render(f"{prefix}{real_idx + 1}. {name}", True, color), (36, 260 + i * 20))
    else:
        screen.blit(fonts["small"].render("Add audio files to the music/ folder", True, GREY), (36, 270))

    pygame.draw.rect(screen, PANEL, (0, 355, W, 45))
    keys = [("P", "Play/Pause"), ("S", "Stop"), ("N", "Next"), ("B", "Prev"), ("Q", "Quit")]
    kx = 15
    for key, label in keys:
        k_surf = fonts["small"].render(f"[{key}]", True, ACCENT)
        l_surf = fonts["small"].render(f" {label}", True, GREY)
        screen.blit(k_surf, (kx, 366))
        screen.blit(l_surf, (kx + k_surf.get_width(), 366))
        kx += k_surf.get_width() + l_surf.get_width() + 10

    if message:
        msg_surf = fonts["small"].render(message, True, GREEN)
        screen.blit(msg_surf, (W - msg_surf.get_width() - 12, 342))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Music Player")

    fonts = {
        "big":   pygame.font.SysFont("Segoe UI", 26, bold=True),
        "med":   pygame.font.SysFont("Segoe UI", 20),
        "small": pygame.font.SysFont("Consolas", 15),
    }

    player = MusicPlayer()
    music_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
    if os.path.isdir(music_folder):
        player.load_folder(music_folder)

    fps_clock = pygame.time.Clock()
    message = ""
    msg_timer = 0

    running = True
    while running:
        dt = fps_clock.tick(30)
        if msg_timer > 0:
            msg_timer -= dt
            if msg_timer <= 0:
                message = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_p:
                    player.toggle_play()
                    message = "Playing…" if player.is_playing else "Paused"
                    msg_timer = 1500
                elif event.key == pygame.K_s:
                    player.stop()
                    message = "Stopped"
                    msg_timer = 1500
                elif event.key == pygame.K_n:
                    player.next_track()
                    message = f"→ {player.track_name()}"
                    msg_timer = 2000
                elif event.key == pygame.K_b:
                    player.prev_track()
                    message = f"← {player.track_name()}"
                    msg_timer = 2000

        player.check_auto_next()
        draw_ui(screen, player, fonts, message if msg_timer > 0 else "")
        pygame.display.flip()

    player.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
