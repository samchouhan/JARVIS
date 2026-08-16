import math
import random
import time
import tkinter as tk

from config import (
    BACKGROUND,
    BOOT_DURATION,
    BOOT_MODULES,
    FRAME_DELAY,
    KEY_STATE_MAP,
    PALETTES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from jarvis_sounds import JarvisSounds
from jarvis_voice import JarvisVoice


class JarvisUI:

    def __init__(self):
        # =========================================================
        # SERVICES
        # =========================================================

        self.sounds = JarvisSounds()
        self.voice = JarvisVoice()

        # =========================================================
        # WINDOW
        # =========================================================

        self.root = tk.Tk()
        self.root.title("JARVIS // RETRO HUD")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = screen_w - WINDOW_WIDTH - 30
        y = screen_h - WINDOW_HEIGHT - 70

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}"
        )

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg=BACKGROUND)

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # =========================================================
        # CENTER
        # =========================================================

        self.cx = WINDOW_WIDTH // 2
        self.cy = WINDOW_HEIGHT // 2 - 20

        # =========================================================
        # ANIMATION
        # =========================================================

        self.state = "sleeping"
        self.state_start_time = time.perf_counter()

        self.angle_fast = 0.0
        self.angle_slow = 0.0
        self.angle_radar = 0.0
        self.time_step = 0.0

        # =========================================================
        # BOOT
        # =========================================================

        self.boot_progress = 0.0
        self.boot_complete = False
        self.last_boot_module = -1

        self.boot_hex = (
            "0x"
            + "".join(
                random.choice("0123456789ABCDEF")
                for _ in range(12)
            )
        )

        # =========================================================
        # KEYBOARD
        # =========================================================

        self.root.bind("<Key>", self._handle_key_events)
        self.root.bind(
            "<Escape>",
            lambda event: self.shutdown(),
        )

        # Start the UI immediately.
        self.animate()

        # Start waking immediately instead of waiting for another
        # animation cycle plus sound/voice initialization.
        self.root.after(1, self.start_boot)

    # =============================================================
    # STATE MANAGEMENT
    # =============================================================

    def set_state(self, new_state):
        if new_state not in PALETTES:
            return

        self.state = new_state
        self.state_start_time = time.perf_counter()

        if new_state == "waking":
            self.boot_progress = 0.0
            self.boot_complete = False
            self.last_boot_module = -1

            self.sounds.play_power(
                stop_after=700,
                root=self.root,
            )

    def start_boot(self):
        self.set_state("waking")

    # =============================================================
    # KEYBOARD
    # =============================================================

    def _handle_key_events(self, event):
        if event.char not in KEY_STATE_MAP:
            return

        state = KEY_STATE_MAP[event.char]

        if state == "speaking":
            self.greet_user()
        else:
            self.set_state(state)

    # =============================================================
    # GREETING
    # =============================================================

    def greet_user(self):
        # Change the HUD to speaking immediately.
        self.set_state("speaking")

        self.voice.greet(
            on_finished=self._voice_finished
        )

    def _voice_finished(self):
        try:
            self.root.after(
                50,
                lambda: self.set_state("listening"),
            )
        except tk.TclError:
            pass

    # =============================================================
    # SHUTDOWN
    # =============================================================

    def shutdown(self):
        try:
            self.voice.stop()
        except Exception:
            pass

        self.sounds.shutdown()

        try:
            self.root.destroy()
        except tk.TclError:
            pass

    # =============================================================
    # ORGANIC BREATHING
    # =============================================================

    def get_organic_breath(self, t, speed=1.2):
        raw = (
            math.exp(math.sin(t * speed))
            - 0.36787944
        ) / 2.35040238

        return raw

    # =============================================================
    # POLAR COORDINATES
    # =============================================================

    def polar(self, radius, angle):
        rad = math.radians(angle)

        return (
            self.cx + math.cos(rad) * radius,
            self.cy + math.sin(rad) * radius,
        )

    # =============================================================
    # MAIN DRAW
    # =============================================================

    def draw_core(self):
        self.canvas.delete("all")

        t = (
            time.perf_counter()
            - self.state_start_time
        )

        main_col, glow_col, bg_accent = PALETTES[self.state]

        breath = self.get_organic_breath(self.time_step)

        if self.state == "waking":
            self._draw_boot_sequence(
                main_col,
                glow_col,
                t,
            )
            return

        self._draw_retro_background(
            main_col,
            bg_accent,
        )

        self._draw_scanlines()
        self._draw_radar(glow_col)
        self._draw_ambient(bg_accent, breath)

        self._draw_rotational_disks(
            main_col,
            glow_col,
            breath,
        )

        self._draw_state_visuals(
            main_col,
            glow_col,
            breath,
            t,
        )

        self._draw_retro_core(
            main_col,
            glow_col,
            breath,
        )

        self._draw_diagnostics(
            main_col,
            glow_col,
        )

        self.canvas.create_text(
            self.cx,
            284,
            text="J A R V I S",
            fill=main_col,
            font=("Courier New", 16, "bold"),
        )

        self.canvas.create_text(
            self.cx,
            305,
            text=f"[ {self.state.upper()} ]",
            fill="#507070",
            font=("Courier New", 9, "bold"),
        )

        self.canvas.create_text(
            self.cx,
            330,
            text="SYS: ONLINE  //  CORE: STABLE",
            fill=glow_col,
            font=("Courier New", 7),
        )

    # =============================================================
    # BACKGROUND
    # =============================================================

    def _draw_retro_background(self, main_col, accent):
        for x in range(0, WINDOW_WIDTH, 20):
            self.canvas.create_line(
                x, 0,
                x, WINDOW_HEIGHT,
                fill="#031316",
            )

        for y in range(0, WINDOW_HEIGHT, 20):
            self.canvas.create_line(
                0, y,
                WINDOW_WIDTH, y,
                fill="#031316",
            )

        self.canvas.create_line(
            self.cx - 150,
            self.cy,
            self.cx + 150,
            self.cy,
            fill="#062027",
        )

        self.canvas.create_line(
            self.cx,
            self.cy - 150,
            self.cx,
            self.cy + 150,
            fill="#062027",
        )

    # =============================================================
    # CRT SCANLINES
    # =============================================================

    def _draw_scanlines(self):
        for y in range(0, WINDOW_HEIGHT, 4):
            self.canvas.create_line(
                0,
                y,
                WINDOW_WIDTH,
                y,
                fill="#031013",
            )

        scan_y = (self.time_step * 28) % WINDOW_HEIGHT

        self.canvas.create_line(
            0,
            scan_y,
            WINDOW_WIDTH,
            scan_y,
            fill="#073b3f",
        )

    # =============================================================
    # RADAR
    # =============================================================

    def _draw_radar(self, color):
        radius = 125
        start = self.angle_radar

        self.canvas.create_arc(
            self.cx - radius,
            self.cy - radius,
            self.cx + radius,
            self.cy + radius,
            start=start,
            extent=18,
            outline=color,
            style="arc",
            width=2,
        )

        x, y = self.polar(radius, start)

        self.canvas.create_line(
            self.cx,
            self.cy,
            x,
            y,
            fill=color,
            width=1,
        )

    # =============================================================
    # AMBIENT GLOW
    # =============================================================

    def _draw_ambient(self, color, breath):
        radius = 108 + breath * 10

        for i in range(4):
            r = radius - i * 10

            self.canvas.create_oval(
                self.cx - r,
                self.cy - r,
                self.cx + r,
                self.cy + r,
                outline=color,
                width=1,
            )

    # =============================================================
    # ROTATIONAL DISKS
    # =============================================================

    def _draw_rotational_disks(
        self,
        main_col,
        glow_col,
        breath,
    ):
        r1 = 94 + breath * 4
        ticks = 32

        for i in range(ticks):
            angle = self.angle_slow + i * (360 / ticks)

            x1, y1 = self.polar(r1 - 4, angle)
            x2, y2 = self.polar(r1 + 4, angle)

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=main_col if i % 4 == 0 else glow_col,
                width=2 if i % 4 == 0 else 1,
            )

        r2 = 80

        for i in range(8):
            start = -self.angle_fast + i * 45

            self.canvas.create_arc(
                self.cx - r2,
                self.cy - r2,
                self.cx + r2,
                self.cy + r2,
                start=start,
                extent=25,
                outline=main_col,
                style="arc",
                width=3,
            )

        r3 = 62

        self.canvas.create_arc(
            self.cx - r3,
            self.cy - r3,
            self.cx + r3,
            self.cy + r3,
            start=self.angle_fast * 1.5,
            extent=120,
            outline=glow_col,
            style="arc",
            width=2,
        )

        self.canvas.create_arc(
            self.cx - r3,
            self.cy - r3,
            self.cx + r3,
            self.cy + r3,
            start=self.angle_fast * 1.5 + 180,
            extent=60,
            outline=glow_col,
            style="arc",
            width=2,
        )

    # =============================================================
    # RETRO CORE
    # =============================================================

    def _draw_retro_core(
        self,
        main_col,
        glow_col,
        breath,
    ):
        core_r = 31 + breath * 5

        self.canvas.create_oval(
            self.cx - core_r,
            self.cy - core_r,
            self.cx + core_r,
            self.cy + core_r,
            fill=BACKGROUND,
            outline=main_col,
            width=3,
        )

        inner_r = core_r - 8

        self.canvas.create_arc(
            self.cx - inner_r,
            self.cy - inner_r,
            self.cx + inner_r,
            self.cy + inner_r,
            start=self.angle_fast,
            extent=100,
            outline=glow_col,
            width=2,
        )

        self.canvas.create_arc(
            self.cx - inner_r,
            self.cy - inner_r,
            self.cx + inner_r,
            self.cy + inner_r,
            start=self.angle_fast + 180,
            extent=100,
            outline=glow_col,
            width=2,
        )

        center_r = 14 + breath * 4

        self.canvas.create_oval(
            self.cx - center_r,
            self.cy - center_r,
            self.cx + center_r,
            self.cy + center_r,
            fill=main_col,
            outline="#bfffff",
            width=1,
        )

        self.canvas.create_line(
            self.cx - 22,
            self.cy,
            self.cx + 22,
            self.cy,
            fill=glow_col,
        )

        self.canvas.create_line(
            self.cx,
            self.cy - 22,
            self.cx,
            self.cy + 22,
            fill=glow_col,
        )

    # =============================================================
    # STATE VISUALS
    # =============================================================

    def _draw_state_visuals(
        self,
        main_col,
        glow_col,
        breath,
        t,
    ):
        if self.state == "listening":
            for i in range(3):
                wave_t = (t * 1.5 + i * 0.8) % 2.0
                wave_r = 35 + wave_t * 38

                self.canvas.create_oval(
                    self.cx - wave_r,
                    self.cy - wave_r,
                    self.cx + wave_r,
                    self.cy + wave_r,
                    outline=main_col,
                    width=1,
                )

        elif self.state == "processing":
            for i in range(6):
                angle = self.angle_fast * 2 + i * 60
                radius = 46 + math.sin(t * 4 + i) * 5

                px, py = self.polar(radius, angle)

                self.canvas.create_rectangle(
                    px - 2,
                    py - 2,
                    px + 2,
                    py + 2,
                    fill="#ffffff",
                    outline="",
                )

        elif self.state == "speaking":
            bars = 24

            for i in range(bars):
                angle = (i / bars) * 360

                amplitude = (
                    abs(math.sin(t * 8 + i))
                    * 15
                )

                x1, y1 = self.polar(42, angle)
                x2, y2 = self.polar(
                    42 + amplitude,
                    angle,
                )

                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=main_col,
                    width=2,
                )

        elif self.state == "success":
            for i in range(8):
                angle = i * 45 + self.angle_fast

                x1, y1 = self.polar(42, angle)
                x2, y2 = self.polar(58, angle)

                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=main_col,
                    width=2,
                )

        elif self.state == "error":
            for _ in range(4):
                gy = self.cy + random.randint(-40, 40)
                offset = random.randint(-10, 10)

                self.canvas.create_line(
                    self.cx - 60 + offset,
                    gy,
                    self.cx + 60 + offset,
                    gy,
                    fill=main_col,
                    width=random.randint(1, 2),
                )

    # =============================================================
    # DIAGNOSTICS
    # =============================================================

    def _draw_diagnostics(self, main_col, glow_col):
        font = ("Courier New", 7)

        left_data = [
            "JRV-02",
            "SYS ONLINE",
            "CORE 87%",
            "MEM 42%",
            "NET LINK",
        ]

        y = 125

        for text in left_data:
            self.canvas.create_text(
                18,
                y,
                text=text,
                anchor="w",
                fill=glow_col,
                font=font,
            )
            y += 11

        right_data = [
            "V.4.7.1",
            "CPU 14%",
            "TEMP 36C",
            "SEC 99%",
            "LINK OK",
        ]

        y = 125

        for text in right_data:
            self.canvas.create_text(
                342,
                y,
                text=text,
                anchor="e",
                fill=glow_col,
                font=font,
            )
            y += 11

        self.canvas.create_text(
            self.cx,
            70,
            text="7A 4F 91 C2 00 FF A1 09 7D 33",
            fill="#16454b",
            font=("Courier New", 7),
        )

        self.canvas.create_text(
            self.cx,
            52,
            text="STARK INDUSTRIES // SYSTEM 01",
            fill=main_col,
            font=("Courier New", 7, "bold"),
        )

    # =============================================================
    # BOOT SEQUENCE
    # =============================================================

    def _draw_boot_sequence(
        self,
        main_col,
        glow_col,
        t,
    ):
        self.boot_progress = min(
            t / BOOT_DURATION,
            1.0,
        )

        progress = self.boot_progress

        current_module = -1

        for i, (_, threshold) in enumerate(BOOT_MODULES):
            if progress >= threshold:
                current_module = i

        if current_module > self.last_boot_module:
            if self.last_boot_module >= 0:
                self.sounds.play("beep")

            self.last_boot_module = current_module

        # Play scan sound once when crossing the middle of boot.
        if (
            self.last_boot_module >= 0
            and 0.48 < progress < 0.51
            and not getattr(self, "_scan_played", False)
        ):
            self.sounds.play("scan")
            self._scan_played = True

        if progress < 0.48:
            self._scan_played = False

        self.canvas.create_rectangle(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            fill="#020708",
            outline="",
        )

        for y in range(0, WINDOW_HEIGHT, 8):
            self.canvas.create_line(
                0,
                y,
                WINDOW_WIDTH,
                y,
                fill="#031214",
            )

        self.canvas.create_text(
            self.cx,
            35,
            text="STARK INDUSTRIES",
            fill=main_col,
            font=("Courier New", 12, "bold"),
        )

        self.canvas.create_text(
            self.cx,
            52,
            text="// J.A.R.V.I.S SYSTEM BOOT //",
            fill=glow_col,
            font=("Courier New", 7),
        )

        boot_radius = 66

        self.canvas.create_oval(
            self.cx - boot_radius,
            self.cy - boot_radius,
            self.cx + boot_radius,
            self.cy + boot_radius,
            outline="#092b2e",
            width=2,
        )

        self.canvas.create_arc(
            self.cx - boot_radius,
            self.cy - boot_radius,
            self.cx + boot_radius,
            self.cy + boot_radius,
            start=90,
            extent=-360 * progress,
            outline=main_col,
            style="arc",
            width=4,
        )

        self.canvas.create_arc(
            self.cx - 55,
            self.cy - 55,
            self.cx + 55,
            self.cy + 55,
            start=self.angle_fast,
            extent=90,
            outline=glow_col,
            style="arc",
            width=2,
        )

        core_radius = 7 + progress * 13

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
            width=2,
        )

        percentage = int(progress * 100)

        self.canvas.create_text(
            self.cx,
            self.cy + 84,
            text=f"BOOT {percentage:03d}%",
            fill=main_col,
            font=("Courier New", 10, "bold"),
        )

        bar_x1 = 55
        bar_x2 = 305
        bar_y = self.cy + 100

        self.canvas.create_rectangle(
            bar_x1,
            bar_y,
            bar_x2,
            bar_y + 8,
            outline=glow_col,
            width=1,
        )

        filled_x = (
            bar_x1
            + (bar_x2 - bar_x1) * progress
        )

        if filled_x > bar_x1:
            self.canvas.create_rectangle(
                bar_x1,
                bar_y,
                filled_x,
                bar_y + 8,
                fill=main_col,
                outline="",
            )

        start_y = 100

        for i, (module, threshold) in enumerate(BOOT_MODULES):
            y = start_y + i * 20

            if progress >= threshold:
                status = "ONLINE"
                status_color = main_col
            elif progress >= threshold - 0.12:
                status = "INIT..."
                status_color = glow_col
            else:
                status = "WAIT"
                status_color = "#244448"

            self.canvas.create_text(
                40,
                y,
                text=module,
                anchor="w",
                fill="#477477",
                font=("Courier New", 8),
            )

            self.canvas.create_text(
                320,
                y,
                text=status,
                anchor="e",
                fill=status_color,
                font=("Courier New", 8, "bold"),
            )

        self.canvas.create_text(
            self.cx,
            320,
            text=self.boot_hex,
            fill="#10383b",
            font=("Courier New", 7),
        )

        if progress >= 1.0:
            self.canvas.create_text(
                self.cx,
                342,
                text="SYSTEM READY",
                fill=main_col,
                font=("Courier New", 9, "bold"),
            )

            if not self.boot_complete:
                self.boot_complete = True

                self.sounds.play("ready1")

                self.root.after(
                    180,
                    lambda: self.sounds.play("ready2"),
                )

                # Start the greeting almost immediately after boot.
                # Voice initialization happens lazily in a background
                # thread, so it does not freeze the HUD.
                self.root.after(
                    120,
                    self.greet_user,
                )

    # =============================================================
    # ANIMATION LOOP
    # =============================================================

    def animate(self):
        self.angle_fast = (self.angle_fast + 2.5) % 360
        self.angle_slow = (self.angle_slow + 0.8) % 360
        self.angle_radar = (self.angle_radar + 1.2) % 360

        self.time_step += 0.035

        self.draw_core()

        self.root.after(
            FRAME_DELAY,
            self.animate,
        )

    # =============================================================
    # RUN
    # =============================================================

    def run(self):
        self.root.mainloop()
