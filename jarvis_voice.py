import threading
import time

import pyttsx3

from config import VOICE_RATE, VOICE_VOLUME


class JarvisVoice:
    """Handles JARVIS speech without blocking the Tkinter UI."""

    def __init__(self):
        self.engine = None
        self.lock = threading.Lock()

    def _initialize(self):
        if self.engine is not None:
            return

        try:
            self.engine = pyttsx3.init("sapi5")
        except Exception:
            self.engine = pyttsx3.init()

        self.engine.setProperty("rate", VOICE_RATE)
        self.engine.setProperty("volume", VOICE_VOLUME)

        # Keep the first available Windows voice, matching the original
        # project behaviour. Voice selection can be customized later.
        try:
            voices = self.engine.getProperty("voices")

            if voices:
                self.engine.setProperty("voice", voices[0].id)
        except Exception:
            pass

    @staticmethod
    def get_greeting():
        hour = time.localtime().tm_hour

        if 5 <= hour < 12:
            return "Good morning, sir."

        if 12 <= hour < 17:
            return "Good afternoon, sir."

        if 17 <= hour < 22:
            return "Good evening, sir."

        return "Good evening, sir."

    def speak(self, text, on_finished=None):
        def worker():
            with self.lock:
                try:
                    self._initialize()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as error:
                    print("Voice error:", error)

            if on_finished is not None:
                on_finished()

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def greet(self, on_finished=None):
        self.speak(
            self.get_greeting(),
            on_finished=on_finished,
        )

    def stop(self):
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception:
                pass
