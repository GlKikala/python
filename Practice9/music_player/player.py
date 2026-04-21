import os
import pygame

SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac")


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = []
        self.current_index = -1
        self.is_playing = False

    def load_folder(self, folder):
        self.playlist = sorted(
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        )
        self.current_index = 0 if self.playlist else -1
        self.is_playing = False
        pygame.mixer.music.stop()
        return len(self.playlist)

    def track_name(self, index=None):
        idx = index if index is not None else self.current_index
        if not self.playlist or idx < 0:
            return "— no track —"
        return os.path.splitext(os.path.basename(self.playlist[idx]))[0]

    def play(self):
        if not self.playlist or self.current_index < 0:
            return
        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def prev_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def toggle_play(self):
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def check_auto_next(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_track()

    @property
    def position_ms(self):
        return pygame.mixer.music.get_pos()

    @property
    def track_count(self):
        return len(self.playlist)
