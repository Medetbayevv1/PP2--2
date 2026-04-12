import pygame
import os

class MusicPlayer:
    """
    Handles playlist management and audio playback.
    Uses pygame.mixer for loading and playing WAV/MP3 files.
    """

    def __init__(self, music_folder="music"):
        # Initialize pygame mixer (audio engine)
        pygame.mixer.init()

        # Load all .wav and .mp3 files from the music folder
        self.playlist = []
        self.load_music(music_folder)

        # Keep track of which song is currently selected
        self.current_index = 0

        # Is music currently playing?
        self.is_playing = False

        # When did we start playing the current track? (for progress bar)
        self.start_ticks = 0

    def load_music(self, folder):
        """Scan the music folder and add supported files to the playlist."""
        if not os.path.exists(folder):
            print(f"Music folder '{folder}' not found!")
            return

        supported = (".wav", ".mp3")
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith(supported):
                full_path = os.path.join(folder, filename)
                self.playlist.append(full_path)

        print(f"Loaded {len(self.playlist)} track(s).")

    def get_track_name(self):
        """Return the display name of the current track (no folder or extension)."""
        if not self.playlist:
            return "No tracks loaded"
        path = self.playlist[self.current_index]
        name = os.path.basename(path)           # e.g. "track1.wav"
        name = os.path.splitext(name)[0]        # e.g. "track1"
        return name.replace("_", " ").title()   # e.g. "Track1"

    def play(self):
        """Load and play the current track from the beginning."""
        if not self.playlist:
            return
        track = self.playlist[self.current_index]
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        self.is_playing = True
        self.start_ticks = pygame.time.get_ticks()  # record start time

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.start_ticks = 0

    def next_track(self):
        """Move to the next track (wraps around to the beginning)."""
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        if self.is_playing:
            self.play()  # auto-play next track if we were already playing

    def previous_track(self):
        """Move to the previous track (wraps around to the end)."""
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def get_elapsed_seconds(self):
        """How many seconds have passed since we started the current track?"""
        if not self.is_playing:
            return 0
        elapsed_ms = pygame.time.get_ticks() - self.start_ticks
        return elapsed_ms // 1000  # convert milliseconds → seconds