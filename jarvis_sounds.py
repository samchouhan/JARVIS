import math
import os
import struct
import wave

import pygame

from config import SOUND_PATH


class JarvisSounds:
    """Handles JARVIS sound generation, loading and playback."""

    def __init__(self):
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512,
        )

        os.makedirs(SOUND_PATH, exist_ok=True)

        self.sounds = {}
        self.power_channel = pygame.mixer.Channel(0)

        self._generate_missing_sounds()
        self._load_sounds()

    def _generate_tone(
        self,
        filename,
        frequency,
        duration,
        volume=0.3,
        end_frequency=None,
    ):
        sample_rate = 44100
        total_samples = int(sample_rate * duration)
        frames = []

        for i in range(total_samples):
            t = i / sample_rate
            progress = i / total_samples

            if end_frequency is not None:
                current_frequency = (
                    frequency
                    + (end_frequency - frequency) * progress
                )
            else:
                current_frequency = frequency

            sample = math.sin(
                2 * math.pi * current_frequency * t
            )

            sample += 0.25 * math.sin(
                2
                * math.pi
                * current_frequency
                * 2
                * t
            )

            fade_in = min(1.0, t / 0.03)
            fade_out = min(1.0, (duration - t) / 0.08)
            envelope = min(fade_in, fade_out)

            sample *= volume * envelope
            value = int(sample * 32767)

            frames.append(struct.pack("<h", value))

        filepath = os.path.join(SOUND_PATH, filename)

        with wave.open(filepath, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b"".join(frames))

    def _generate_missing_sounds(self):
        sounds = {
            "power.wav": (55, 1.4, 0.45, 180),
            "beep.wav": (850, 0.08, 0.30, None),
            "beep2.wav": (1200, 0.06, 0.25, None),
            "scan.wav": (400, 0.7, 0.22, 1400),
            "ready1.wav": (500, 0.12, 0.30, 900),
            "ready2.wav": (1200, 0.20, 0.32, 1800),
            "error.wav": (400, 0.25, 0.30, 180),
            "listen.wav": (700, 0.10, 0.22, 1000),
        }

        for filename, values in sounds.items():
            filepath = os.path.join(SOUND_PATH, filename)

            # Important: do not regenerate WAV files every time JARVIS starts.
            if not os.path.exists(filepath):
                self._generate_tone(filename, *values)

    def _load_sounds(self):
        for filename in (
            "power.wav",
            "beep.wav",
            "beep2.wav",
            "scan.wav",
            "ready1.wav",
            "ready2.wav",
            "error.wav",
            "listen.wav",
        ):
            filepath = os.path.join(SOUND_PATH, filename)

            if os.path.exists(filepath):
                name = os.path.splitext(filename)[0]
                self.sounds[name] = pygame.mixer.Sound(filepath)

    def play(self, name):
        sound = self.sounds.get(name)

        if sound is not None:
            sound.play()

    def play_power(self, stop_after=700, root=None):
        sound = self.sounds.get("power")

        if sound is None:
            return

        self.power_channel.play(sound)

        if root is not None:
            root.after(stop_after, self.power_channel.stop)

    def stop(self):
        try:
            self.power_channel.stop()
            pygame.mixer.stop()
        except pygame.error:
            pass

    def shutdown(self):
        self.stop()

        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
