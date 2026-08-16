import math
import random
import time
import tkinter as tk
import pygame
import wave
import struct
import os
import pyttsx3
import threading


class JarvisUI:

    def __init__(self):

        # =========================================================
        # SOUND ENGINE
        # =========================================================

        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )

        self.sound_path = "jarvis_sounds"

        if not os.path.exists(self.sound_path):
            os.makedirs(self.sound_path)

        self.generate_sounds()

        # Dedicated channel for power-up sound
        self.power_channel = pygame.mixer.Channel(0)

        # =========================================================
        # JARVIS VOICE ENGINE
        # =========================================================

        try:

            self.voice_engine = pyttsx3.init("sapi5")

        except Exception:

            self.voice_engine = pyttsx3.init()

        self.voice_engine.setProperty(
            "rate",
            145
        )

        self.voice_engine.setProperty(
            "volume",
            1.0
        )

        # Try to select the first available Windows voice
        try:

            voices = self.voice_engine.getProperty(
                "voices"
            )

            if voices:

                self.voice_engine.setProperty(
                    "voice",
                    voices[0].id
                )

        except Exception:
            pass

        # Prevent multiple speech threads
        self.speaking_lock = threading.Lock()

        # =========================================================
        # WINDOW
        # =========================================================

        self.root = tk.Tk()

        self.root.title(
            "JARVIS // RETRO HUD"
        )

        width = 360
        height = 360

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = screen_w - width - 30
        y = screen_h - height - 70

        self.root.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        self.root.attributes(
            "-topmost",
            True
        )

        self.root.overrideredirect(
            True
        )

        self.root.configure(
            bg="#020b0d"
        )

        # =========================================================
        # CANVAS
        # =========================================================

        self.canvas = tk.Canvas(

            self.root,

            width=width,
            height=height,

            bg="#020b0d",

            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # =========================================================
        # CENTER
        # =========================================================

        self.cx = width // 2

        self.cy = (
            height // 2
            - 20
        )

        # =========================================================
        # ANIMATION
        # =========================================================

        self.state = "sleeping"

        self.state_start_time = (
            time.time()
        )

        self.angle_fast = 0.0
        self.angle_slow = 0.0
        self.angle_radar = 0.0

        self.time_step = 0.0

        # =========================================================
        # BOOT SYSTEM
        # =========================================================

        self.boot_progress = 0.0

        self.boot_complete = False

        self.boot_modules = [

            ("POWER CORE", 0.12),

            ("MEMORY ARRAY", 0.25),

            ("NEURAL NETWORK", 0.40),

            ("VOICE MODULE", 0.55),

            ("SENSOR ARRAY", 0.70),

            ("SECURITY SYSTEM", 0.84),

            ("JARVIS CORE", 1.00),

        ]

        self.last_boot_module = -1

        # =========================================================
        # PALETTES
        # =========================================================

        self.palettes = {

            "sleeping": (
                "#0088aa",
                "#005577",
                "#032025"
            ),

            "waking": (
                "#00ffff",
                "#008888",
                "#063333"
            ),

            "listening": (
                "#00ffcc",
                "#008877",
                "#00332c"
            ),

            "processing": (
                "#c084ff",
                "#673b88",
                "#251536"
            ),

            "speaking": (
                "#ffb000",
                "#996600",
                "#332000"
            ),

            "success": (
                "#00ff66",
                "#008833",
                "#002211"
            ),

            "error": (
                "#ff3344",
                "#881122",
                "#33070c"
            ),
        }

        # =========================================================
        # KEYBOARD CONTROLS
        # =========================================================

        self.root.bind(
            "<Key>",
            self._handle_key_events
        )

        self.root.bind(
            "<Escape>",
            lambda event: self.shutdown()
        )

        # =========================================================
        # START ANIMATION
        # =========================================================

        self.animate()

        # =========================================================
        # AUTOMATIC BOOT
        # =========================================================

        self.root.after(
            100,
            lambda: self.set_state(
                "waking"
            )
        )

    # =============================================================
    # SOUND GENERATION
    # =============================================================

    def generate_tone(
        self,
        filename,
        frequency,
        duration,
        volume=0.3,
        end_frequency=None
    ):

        sample_rate = 44100

        total_samples = int(
            sample_rate * duration
        )

        frames = []

        for i in range(
            total_samples
        ):

            t = (
                i / sample_rate
            )

            progress = (
                i / total_samples
            )

            if end_frequency is not None:

                current_frequency = (

                    frequency

                    + (

                        end_frequency
                        - frequency

                    ) * progress
                )

            else:

                current_frequency = (
                    frequency
                )

            # -----------------------------------------------------
            # MAIN OSCILLATOR
            # -----------------------------------------------------

            sample = math.sin(

                2
                * math.pi
                * current_frequency
                * t
            )

            # -----------------------------------------------------
            # HARMONIC
            # -----------------------------------------------------

            sample += (
                0.25
                * math.sin(

                    2
                    * math.pi
                    * current_frequency
                    * 2
                    * t
                )
            )

            # -----------------------------------------------------
            # ENVELOPE
            # -----------------------------------------------------

            fade_in = min(
                1.0,
                t / 0.03
            )

            fade_out = min(
                1.0,
                (duration - t) / 0.08
            )

            envelope = min(
                fade_in,
                fade_out
            )

            sample *= (
                volume
                * envelope
            )

            value = int(
                sample * 32767
            )

            frames.append(
                struct.pack(
                    "<h",
                    value
                )
            )

        filepath = os.path.join(
            self.sound_path,
            filename
        )

        with wave.open(
            filepath,
            "wb"
        ) as wav:

            wav.setnchannels(1)

            wav.setsampwidth(2)

            wav.setframerate(
                sample_rate
            )

            wav.writeframes(
                b"".join(frames)
            )

    # =============================================================
    # GENERATE ALL JARVIS SOUNDS
    # =============================================================

    def generate_sounds(self):

        # ---------------------------------------------------------
        # POWER-UP
        # ---------------------------------------------------------

        self.generate_tone(

            "power.wav",

            55,

            1.4,

            0.45,

            180
        )

        # ---------------------------------------------------------
        # MODULE BEEP
        # ---------------------------------------------------------

        self.generate_tone(

            "beep.wav",

            850,

            0.08,

            0.30
        )

        # ---------------------------------------------------------
        # SECONDARY BEEP
        # ---------------------------------------------------------

        self.generate_tone(

            "beep2.wav",

            1200,

            0.06,

            0.25
        )

        # ---------------------------------------------------------
        # SCANNING
        # ---------------------------------------------------------

        self.generate_tone(

            "scan.wav",

            400,

            0.7,

            0.22,

            1400
        )

        # ---------------------------------------------------------
        # SYSTEM READY
        # ---------------------------------------------------------

        self.generate_tone(

            "ready1.wav",

            500,

            0.12,

            0.3,

            900
        )

        self.generate_tone(

            "ready2.wav",

            1200,

            0.20,

            0.32,

            1800
        )

        # ---------------------------------------------------------
        # ERROR
        # ---------------------------------------------------------

        self.generate_tone(

            "error.wav",

            400,

            0.25,

            0.3,

            180
        )

        # ---------------------------------------------------------
        # LISTENING
        # ---------------------------------------------------------

        self.generate_tone(

            "listen.wav",

            700,

            0.10,

            0.22,

            1000
        )

    # =============================================================
    # PLAY SOUND
    # =============================================================

    def play_sound(
        self,
        filename
    ):

        filepath = os.path.join(

            self.sound_path,

            filename
        )

        if os.path.exists(
            filepath
        ):

            sound = pygame.mixer.Sound(
                filepath
            )

            sound.play()

    # =============================================================
    # JARVIS GREETING
    # =============================================================

    def greet_user(self):

        current_hour = (
            time.localtime().tm_hour
        )

        if 5 <= current_hour < 12:

            greeting = (
                "Good morning, sir."
            )

        elif 12 <= current_hour < 17:

            greeting = (
                "Good afternoon, sir."
            )

        elif 17 <= current_hour < 22:

            greeting = (
                "Good evening, sir."
            )

        else:

            greeting = (
                "Good evening, sir."
            )

        # Change visual state immediately

        self.set_state(
            "speaking"
        )

        # ---------------------------------------------------------
        # SPEECH THREAD
        # ---------------------------------------------------------

        def speak():

            with self.speaking_lock:

                try:

                    self.voice_engine.say(
                        greeting
                    )

                    self.voice_engine.runAndWait()

                except Exception as e:

                    print(
                        "Voice error:",
                        e
                    )

            # -----------------------------------------------------
            # Return to LISTENING
            # -----------------------------------------------------

            try:

                self.root.after(

                    100,

                    lambda:
                    self.set_state(
                        "listening"
                    )
                )

            except tk.TclError:

                pass

        threading.Thread(

            target=speak,

            daemon=True

        ).start()

    # =============================================================
    # SHUTDOWN
    # =============================================================

    def shutdown(self):

        try:

            self.voice_engine.stop()

        except Exception:

            pass

        pygame.mixer.stop()

        pygame.mixer.quit()

        self.root.destroy()

    # =============================================================
    # STATE MANAGEMENT
    # =============================================================

    def set_state(
        self,
        new_state
    ):

        if new_state not in self.palettes:

            return

        self.state = new_state

        self.state_start_time = (
            time.time()
        )

        # =========================================================
        # START BOOT SEQUENCE
        # =========================================================

        if new_state == "waking":

            self.boot_progress = 0.0

            self.boot_complete = False

            self.last_boot_module = -1

            # -----------------------------------------------------
            # POWER-UP SOUND
            # -----------------------------------------------------

            filepath = os.path.join(

                self.sound_path,

                "power.wav"
            )

            if os.path.exists(
                filepath
            ):

                power_sound = (
                    pygame.mixer.Sound(
                        filepath
                    )
                )

                self.power_channel.play(
                    power_sound
                )

                # Stop power hum after 700ms

                self.root.after(

                    700,

                    self.power_channel.stop
                )

    # =============================================================
    # KEYBOARD
    # =============================================================

    def _handle_key_events(
        self,
        event
    ):

        key_map = {

            "1": "sleeping",

            "2": "waking",

            "3": "listening",

            "4": "processing",

            "5": "speaking",

            "6": "success",

            "7": "error"

        }

        if event.char in key_map:

            self.set_state(
                key_map[event.char]
            )

            # If manually switching to speaking,
            # trigger greeting

            if event.char == "5":

                self.greet_user()

    # =============================================================
    # ORGANIC BREATHING
    # =============================================================

    def get_organic_breath(
        self,
        t,
        speed=1.2
    ):

        raw = (

            math.exp(

                math.sin(

                    t * speed
                )
            )

            - 0.36787944

        ) / 2.35040238

        return raw

    # =============================================================
    # POLAR COORDINATES
    # =============================================================

    def polar(
        self,
        radius,
        angle
    ):

        rad = math.radians(
            angle
        )

        return (

            self.cx
            + math.cos(rad)
            * radius,

            self.cy
            + math.sin(rad)
            * radius
        )

    # =============================================================
    # MAIN DRAW
    # =============================================================

    def draw_core(self):

        self.canvas.delete(
            "all"
        )

        t = (

            time.time()
            - self.state_start_time
        )

        main_col, glow_col, bg_accent = (

            self.palettes[
                self.state
            ]
        )

        breath = (
            self.get_organic_breath(
                self.time_step
            )
        )

        # ---------------------------------------------------------
        # BOOT
        # ---------------------------------------------------------

        if self.state == "waking":

            self._draw_boot_sequence(

                main_col,

                glow_col,

                t
            )

            return

        # ---------------------------------------------------------
        # NORMAL HUD
        # ---------------------------------------------------------

        self._draw_retro_background(

            main_col,

            bg_accent
        )

        self._draw_scanlines()

        self._draw_radar(
            glow_col
        )

        self._draw_ambient(

            bg_accent,

            breath
        )

        self._draw_rotational_disks(

            main_col,

            glow_col,

            breath
        )

        self._draw_state_visuals(

            main_col,

            glow_col,

            breath,

            t
        )

        self._draw_retro_core(

            main_col,

            glow_col,

            breath
        )

        self._draw_diagnostics(

            main_col,

            glow_col
        )

        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------

        self.canvas.create_text(

            self.cx,

            284,

            text="J A R V I S",

            fill=main_col,

            font=(

                "Courier New",

                16,

                "bold"
            )
        )

        # ---------------------------------------------------------
        # STATE
        # ---------------------------------------------------------

        self.canvas.create_text(

            self.cx,

            305,

            text=(

                f"[ "

                f"{self.state.upper()}"

                f" ]"
            ),

            fill="#507070",

            font=(

                "Courier New",

                9,

                "bold"
            )
        )

        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------

        self.canvas.create_text(

            self.cx,

            330,

            text=(

                "SYS: ONLINE"

                "  //  "

                "CORE: STABLE"
            ),

            fill=glow_col,

            font=(

                "Courier New",

                7
            )
        )

    # =============================================================
    # RETRO BACKGROUND
    # =============================================================

    def _draw_retro_background(

        self,
        main_col,
        accent
    ):

        # Vertical grid

        for x in range(
            0,
            360,
            20
        ):

            self.canvas.create_line(

                x,
                0,

                x,
                360,

                fill="#031316"
            )

        # Horizontal grid

        for y in range(
            0,
            360,
            20
        ):

            self.canvas.create_line(

                0,
                y,

                360,
                y,

                fill="#031316"
            )

        # Center horizontal

        self.canvas.create_line(

            self.cx - 150,

            self.cy,

            self.cx + 150,

            self.cy,

            fill="#062027"
        )

        # Center vertical

        self.canvas.create_line(

            self.cx,

            self.cy - 150,

            self.cx,

            self.cy + 150,

            fill="#062027"
        )

    # =============================================================
    # CRT SCANLINES
    # =============================================================

    def _draw_scanlines(self):

        for y in range(
            0,
            360,
            4
        ):

            self.canvas.create_line(

                0,
                y,

                360,
                y,

                fill="#031013"
            )

        scan_y = (

            self.time_step
            * 28
        ) % 360

        self.canvas.create_line(

            0,
            scan_y,

            360,
            scan_y,

            fill="#073b3f"
        )

    # =============================================================
    # RADAR
    # =============================================================

    def _draw_radar(
        self,
        color
    ):

        radius = 125

        start = (
            self.angle_radar
        )

        self.canvas.create_arc(

            self.cx - radius,

            self.cy - radius,

            self.cx + radius,

            self.cy + radius,

            start=start,

            extent=18,

            outline=color,

            style="arc",

            width=2
        )

        x, y = self.polar(

            radius,

            start
        )

        self.canvas.create_line(

            self.cx,

            self.cy,

            x,

            y,

            fill=color,

            width=1
        )

    # =============================================================
    # AMBIENT GLOW
    # =============================================================

    def _draw_ambient(

        self,
        color,
        breath
    ):

        radius = (

            108

            + breath * 10
        )

        for i in range(4):

            r = (

                radius
                - i * 10
            )

            self.canvas.create_oval(

                self.cx - r,

                self.cy - r,

                self.cx + r,

                self.cy + r,

                outline=color,

                width=1
            )

    # =============================================================
    # ROTATIONAL DISKS
    # =============================================================

    def _draw_rotational_disks(

        self,
        main_col,
        glow_col,
        breath
    ):

        # ---------------------------------------------------------
        # OUTER TICKS
        # ---------------------------------------------------------

        r1 = (

            94

            + breath * 4
        )

        ticks = 32

        for i in range(ticks):

            angle = (

                self.angle_slow

                + i * (
                    360 / ticks
                )
            )

            x1, y1 = self.polar(

                r1 - 4,

                angle
            )

            x2, y2 = self.polar(

                r1 + 4,

                angle
            )

            self.canvas.create_line(

                x1,

                y1,

                x2,

                y2,

                fill=(

                    main_col

                    if i % 4 == 0

                    else glow_col
                ),

                width=(

                    2

                    if i % 4 == 0

                    else 1
                )
            )

        # ---------------------------------------------------------
        # SEGMENTED RING
        # ---------------------------------------------------------

        r2 = 80

        for i in range(8):

            start = (

                -self.angle_fast

                + i * 45
            )

            self.canvas.create_arc(

                self.cx - r2,

                self.cy - r2,

                self.cx + r2,

                self.cy + r2,

                start=start,

                extent=25,

                outline=main_col,

                style="arc",

                width=3
            )

        # ---------------------------------------------------------
        # INNER RING
        # ---------------------------------------------------------

        r3 = 62

        self.canvas.create_arc(

            self.cx - r3,

            self.cy - r3,

            self.cx + r3,

            self.cy + r3,

            start=(

                self.angle_fast
                * 1.5
            ),

            extent=120,

            outline=glow_col,

            style="arc",

            width=2
        )

        self.canvas.create_arc(

            self.cx - r3,

            self.cy - r3,

            self.cx + r3,

            self.cy + r3,

            start=(

                self.angle_fast
                * 1.5

                + 180
            ),

            extent=60,

            outline=glow_col,

            style="arc",

            width=2
        )

    # =============================================================
    # RETRO CORE
    # =============================================================

    def _draw_retro_core(

        self,
        main_col,
        glow_col,
        breath
    ):

        core_r = (

            31

            + breath * 5
        )

        # ---------------------------------------------------------
        # OUTER REACTOR
        # ---------------------------------------------------------

        self.canvas.create_oval(

            self.cx - core_r,

            self.cy - core_r,

            self.cx + core_r,

            self.cy + core_r,

            fill="#020b0d",

            outline=main_col,

            width=3
        )

        # ---------------------------------------------------------
        # INNER ARCS
        # ---------------------------------------------------------

        inner_r = (

            core_r - 8
        )

        self.canvas.create_arc(

            self.cx - inner_r,

            self.cy - inner_r,

            self.cx + inner_r,

            self.cy + inner_r,

            start=self.angle_fast,

            extent=100,

            outline=glow_col,

            width=2
        )

        self.canvas.create_arc(

            self.cx - inner_r,

            self.cy - inner_r,

            self.cx + inner_r,

            self.cy + inner_r,

            start=(

                self.angle_fast
                + 180
            ),

            extent=100,

            outline=glow_col,

            width=2
        )

        # ---------------------------------------------------------
        # ENERGY CORE
        # ---------------------------------------------------------

        center_r = (

            14

            + breath * 4
        )

        self.canvas.create_oval(

            self.cx - center_r,

            self.cy - center_r,

            self.cx + center_r,

            self.cy + center_r,

            fill=main_col,

            outline="#bfffff",

            width=1
        )

        # ---------------------------------------------------------
        # CROSSHAIR
        # ---------------------------------------------------------

        self.canvas.create_line(

            self.cx - 22,

            self.cy,

            self.cx + 22,

            self.cy,

            fill=glow_col
        )

        self.canvas.create_line(

            self.cx,

            self.cy - 22,

            self.cx,

            self.cy + 22,

            fill=glow_col
        )

    # =============================================================
    # STATE VISUALS
    # =============================================================

    def _draw_state_visuals(

        self,
        main_col,
        glow_col,
        breath,
        t
    ):

        # ---------------------------------------------------------
        # LISTENING
        # ---------------------------------------------------------

        if self.state == "listening":

            for i in range(3):

                wave_t = (

                    t * 1.5

                    + i * 0.8

                ) % 2.0

                wave_r = (

                    35

                    + wave_t * 38
                )

                self.canvas.create_oval(

                    self.cx - wave_r,

                    self.cy - wave_r,

                    self.cx + wave_r,

                    self.cy + wave_r,

                    outline=main_col,

                    width=1
                )

        # ---------------------------------------------------------
        # PROCESSING
        # ---------------------------------------------------------

        elif self.state == "processing":

            for i in range(6):

                angle = (

                    self.angle_fast * 2

                    + i * 60
                )

                radius = (

                    46

                    + math.sin(

                        t * 4 + i

                    ) * 5
                )

                px, py = self.polar(

                    radius,

                    angle
                )

                self.canvas.create_rectangle(

                    px - 2,

                    py - 2,

                    px + 2,

                    py + 2,

                    fill="#ffffff",

                    outline=""
                )

        # ---------------------------------------------------------
        # SPEAKING
        # ---------------------------------------------------------

        elif self.state == "speaking":

            bars = 24

            for i in range(bars):

                angle = (

                    i / bars
                ) * 360

                amplitude = (

                    abs(

                        math.sin(

                            t * 8 + i

                        )
                    )

                    * 15
                )

                x1, y1 = self.polar(

                    42,

                    angle
                )

                x2, y2 = self.polar(

                    42 + amplitude,

                    angle
                )

                self.canvas.create_line(

                    x1,

                    y1,

                    x2,

                    y2,

                    fill=main_col,

                    width=2
                )

        # ---------------------------------------------------------
        # SUCCESS
        # ---------------------------------------------------------

        elif self.state == "success":

            for i in range(8):

                angle = (

                    i * 45

                    + self.angle_fast
                )

                x1, y1 = self.polar(

                    42,

                    angle
                )

                x2, y2 = self.polar(

                    58,

                    angle
                )

                self.canvas.create_line(

                    x1,

                    y1,

                    x2,

                    y2,

                    fill=main_col,

                    width=2
                )

        # ---------------------------------------------------------
        # ERROR
        # ---------------------------------------------------------

        elif self.state == "error":

            for _ in range(4):

                gy = (

                    self.cy

                    + random.randint(
                        -40,
                        40
                    )
                )

                offset = random.randint(

                    -10,

                    10
                )

                self.canvas.create_line(

                    self.cx - 60 + offset,

                    gy,

                    self.cx + 60 + offset,

                    gy,

                    fill=main_col,

                    width=random.randint(
                        1,
                        2
                    )
                )

    # =============================================================
    # DIAGNOSTICS
    # =============================================================

    def _draw_diagnostics(

        self,
        main_col,
        glow_col
    ):

        font = (

            "Courier New",

            7
        )

        # ---------------------------------------------------------
        # LEFT
        # ---------------------------------------------------------

        left_data = [

            "JRV-02",

            "SYS ONLINE",

            "CORE 87%",

            "MEM 42%",

            "NET LINK"

        ]

        y = 125

        for text in left_data:

            self.canvas.create_text(

                18,

                y,

                text=text,

                anchor="w",

                fill=glow_col,

                font=font
            )

            y += 11

        # ---------------------------------------------------------
        # RIGHT
        # ---------------------------------------------------------

        right_data = [

            "V.4.7.1",

            "CPU 14%",

            "TEMP 36C",

            "SEC 99%",

            "LINK OK"

        ]

        y = 125

        for text in right_data:

            self.canvas.create_text(

                342,

                y,

                text=text,

                anchor="e",

                fill=glow_col,

                font=font
            )

            y += 11

        # ---------------------------------------------------------
        # HEX DATA
        # ---------------------------------------------------------

        hex_data = (

            "7A 4F 91 C2 00 FF "

            "A1 09 7D 33"
        )

        self.canvas.create_text(

            self.cx,

            70,

            text=hex_data,

            fill="#16454b",

            font=(

                "Courier New",

                7
            )
        )

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        self.canvas.create_text(

            self.cx,

            52,

            text=(

                "STARK INDUSTRIES"

                " // SYSTEM 01"
            ),

            fill=main_col,

            font=(

                "Courier New",

                7,

                "bold"
            )
        )

    # =============================================================
    # BOOT SEQUENCE
    # =============================================================

    def _draw_boot_sequence(

        self,
        main_col,
        glow_col,
        t
    ):

        # =========================================================
        # BOOT PROGRESS
        # =========================================================

        # 5 SECOND BOOT

        self.boot_progress = min(

            t / 5.0,

            1.0
        )

        progress = (
            self.boot_progress
        )

        # =========================================================
        # CURRENT MODULE
        # =========================================================

        current_module = -1

        for i, (

            module,

            threshold

        ) in enumerate(

            self.boot_modules

        ):

            if progress >= threshold:

                current_module = i

        # =========================================================
        # MODULE BEEP
        # =========================================================

        if (

            current_module
            > self.last_boot_module

        ):

            if self.last_boot_module >= 0:

                self.play_sound(
                    "beep.wav"
                )

            self.last_boot_module = (

                current_module
            )

        # =========================================================
        # SCAN SOUND
        # =========================================================

        if (

            0.48
            < progress
            < 0.51

        ):

            self.play_sound(
                "scan.wav"
            )

        # =========================================================
        # BACKGROUND
        # =========================================================

        self.canvas.create_rectangle(

            0,

            0,

            360,

            360,

            fill="#020708",

            outline=""
        )

        # =========================================================
        # CRT GRID
        # =========================================================

        for y in range(

            0,

            360,

            8
        ):

            self.canvas.create_line(

                0,

                y,

                360,

                y,

                fill="#031214"
            )

        # =========================================================
        # HEADER
        # =========================================================

        self.canvas.create_text(

            self.cx,

            35,

            text="STARK INDUSTRIES",

            fill=main_col,

            font=(

                "Courier New",

                12,

                "bold"
            )
        )

        self.canvas.create_text(

            self.cx,

            52,

            text=(

                "// J.A.R.V.I.S SYSTEM BOOT //"

            ),

            fill=glow_col,

            font=(

                "Courier New",

                7
            )
        )

        # =========================================================
        # REACTOR
        # =========================================================

        boot_radius = 66

        self.canvas.create_oval(

            self.cx - boot_radius,

            self.cy - boot_radius,

            self.cx + boot_radius,

            self.cy + boot_radius,

            outline="#092b2e",

            width=2
        )

        # =========================================================
        # PROGRESS ARC
        # =========================================================

        self.canvas.create_arc(

            self.cx - boot_radius,

            self.cy - boot_radius,

            self.cx + boot_radius,

            self.cy + boot_radius,

            start=90,

            extent=-360 * progress,

            outline=main_col,

            style="arc",

            width=4
        )

        # =========================================================
        # ROTATING RING
        # =========================================================

        self.canvas.create_arc(

            self.cx - 55,

            self.cy - 55,

            self.cx + 55,

            self.cy + 55,

            start=self.angle_fast,

            extent=90,

            outline=glow_col,

            style="arc",

            width=2
        )

        # =========================================================
        # CORE
        # =========================================================

        core_radius = (

            7

            + progress * 13
        )

        core_color = (

            main_col

            if progress > 0.15

            else "#04191b"
        )

        self.canvas.create_oval(

            self.cx - core_radius,

            self.cy - core_radius,

            self.cx + core_radius,

            self.cy + core_radius,

            fill=core_color,

            outline=glow_col,

            width=2
        )

        # =========================================================
        # BOOT PERCENTAGE
        # =========================================================

        percentage = int(

            progress * 100
        )

        self.canvas.create_text(

            self.cx,

            self.cy + 84,

            text=(

                f"BOOT "

                f"{percentage:03d}%"
            ),

            fill=main_col,

            font=(

                "Courier New",

                10,

                "bold"
            )
        )

        # =========================================================
        # PROGRESS BAR
        # =========================================================

        bar_x1 = 55

        bar_x2 = 305

        bar_y = (

            self.cy + 100
        )

        self.canvas.create_rectangle(

            bar_x1,

            bar_y,

            bar_x2,

            bar_y + 8,

            outline=glow_col,

            width=1
        )

        filled_x = (

            bar_x1

            + (

                bar_x2
                - bar_x1

            ) * progress
        )

        if filled_x > bar_x1:

            self.canvas.create_rectangle(

                bar_x1,

                bar_y,

                filled_x,

                bar_y + 8,

                fill=main_col,

                outline=""
            )

        # =========================================================
        # MODULES
        # =========================================================

        start_y = 100

        for i, (

            module,

            threshold

        ) in enumerate(

            self.boot_modules

        ):

            y = (

                start_y

                + i * 20
            )

            if progress >= threshold:

                status = "ONLINE"

                status_color = main_col

            elif progress >= (

                threshold - 0.12

            ):

                status = "INIT..."

                status_color = glow_col

            else:

                status = "WAIT"

                status_color = "#244448"

            # -----------------------------------------------------
            # MODULE NAME
            # -----------------------------------------------------

            self.canvas.create_text(

                40,

                y,

                text=module,

                anchor="w",

                fill="#477477",

                font=(

                    "Courier New",

                    8
                )
            )

            # -----------------------------------------------------
            # STATUS
            # -----------------------------------------------------

            self.canvas.create_text(

                320,

                y,

                text=status,

                anchor="e",

                fill=status_color,

                font=(

                    "Courier New",

                    8,

                    "bold"
                )
            )

        # =========================================================
        # HEX DATA
        # =========================================================

        hex_data = (

            "0x"

            + "".join(

                random.choice(

                    "0123456789ABCDEF"

                )

                for _ in range(12)
            )
        )

        self.canvas.create_text(

            self.cx,

            320,

            text=hex_data,

            fill="#10383b",

            font=(

                "Courier New",

                7
            )
        )

        # =========================================================
        # SYSTEM READY
        # =========================================================

        if progress >= 1.0:

            self.canvas.create_text(

                self.cx,

                342,

                text="SYSTEM READY",

                fill=main_col,

                font=(

                    "Courier New",

                    9,

                    "bold"
                )
            )

            # -----------------------------------------------------
            # ONLY EXECUTE ONCE
            # -----------------------------------------------------

            if not self.boot_complete:

                self.boot_complete = True

                # -------------------------------------------------
                # READY SOUNDS
                # -------------------------------------------------

                self.play_sound(
                    "ready1.wav"
                )

                self.root.after(

                    180,

                    lambda:
                    self.play_sound(
                        "ready2.wav"
                    )
                )

                # -------------------------------------------------
                # GREETING
                #
                # Only 100ms delay now.
                # Speech runs in its own thread.
                # -------------------------------------------------

                self.root.after(

                    100,

                    self.greet_user
                )

    # =============================================================
    # ANIMATION LOOP
    # =============================================================

    def animate(self):

        self.angle_fast = (

            self.angle_fast

            + 2.5

        ) % 360

        self.angle_slow = (

            self.angle_slow

            + 0.8

        ) % 360

        self.angle_radar = (

            self.angle_radar

            + 1.2

        ) % 360

        self.time_step += 0.035

        self.draw_core()

        self.root.after(

            16,

            self.animate
        )

    # =============================================================
    # RUN
    # =============================================================

    def run(self):

        self.root.mainloop()


# ================================================================
# PROGRAM ENTRY
# ================================================================

if __name__ == "__main__":

    app = JarvisUI()

    app.run()