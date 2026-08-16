#This version design of Jarvis consists of manual keysetups and retro style design
import math
import random
import time
import tkinter as tk


class JarvisUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("JARVIS // RETRO HUD")

        # ---------------------------------------------------------
        # WINDOW
        # ---------------------------------------------------------

        width, height = 360, 360

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = screen_w - width - 30
        y = screen_h - height - 70

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.root.configure(bg="#020b0d")

        # ---------------------------------------------------------
        # CANVAS
        # ---------------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="#020b0d",
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)

        # ---------------------------------------------------------
        # CENTER
        # ---------------------------------------------------------

        self.cx = width // 2
        self.cy = height // 2 - 20

        # ---------------------------------------------------------
        # ANIMATION
        # ---------------------------------------------------------

        self.state = "processing"

        self.state_start_time = time.time()

        self.angle_fast = 0.0
        self.angle_slow = 0.0
        self.angle_radar = 0.0

        self.time_step = 0.0

        # CRT flicker
        self.flicker = 0

        # Randomized diagnostic values
        self.cpu_value = 14
        self.power_value = 87

        # ---------------------------------------------------------
        # RETRO COLOR PALETTES
        # ---------------------------------------------------------

        self.palettes = {

            # Classic terminal blue
            "sleeping": (
                "#0088aa",
                "#005577",
                "#032025"
            ),

            # Bright CRT cyan
            "waking": (
                "#00ffff",
                "#008888",
                "#063333"
            ),

            # Radar cyan
            "listening": (
                "#00ffcc",
                "#008877",
                "#00332c"
            ),

            # Old computer purple
            "processing": (
                "#c084ff",
                "#673b88",
                "#251536"
            ),

            # Amber terminal
            "speaking": (
                "#ffb000",
                "#996600",
                "#332000"
            ),

            # Green terminal
            "success": (
                "#00ff66",
                "#008833",
                "#002211"
            ),

            # Red warning terminal
            "error": (
                "#ff3344",
                "#881122",
                "#33070c"
            ),
        }

        # ---------------------------------------------------------
        # KEYBOARD TESTING
        # ---------------------------------------------------------

        self.root.bind(
            "<Key>",
            self._handle_key_events
        )

        self.root.bind(
            "<Escape>",
            lambda e: self.root.destroy()
        )

        # ---------------------------------------------------------
        # START
        # ---------------------------------------------------------

        self.animate()

    # =============================================================
    # STATE
    # =============================================================

    def set_state(self, new_state):

        if new_state in self.palettes:

            self.state = new_state
            self.state_start_time = time.time()

    def _handle_key_events(self, event):

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
                math.sin(t * speed)
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

        rad = math.radians(angle)

        return (
            self.cx + math.cos(rad) * radius,
            self.cy + math.sin(rad) * radius
        )

    # =============================================================
    # MAIN DRAW
    # =============================================================

    def draw_core(self):

        self.canvas.delete("all")

        t = (
            time.time()
            - self.state_start_time
        )

        main_col, glow_col, bg_accent = (
            self.palettes[self.state]
        )

        breath = self.get_organic_breath(
            self.time_step
        )

        # ---------------------------------------------------------
        # BACKGROUND
        # ---------------------------------------------------------

        self._draw_retro_background(
            main_col,
            bg_accent
        )

        # ---------------------------------------------------------
        # CRT EFFECT
        # ---------------------------------------------------------

        self._draw_scanlines()

        # ---------------------------------------------------------
        # RADAR SWEEP
        # ---------------------------------------------------------

        self._draw_radar(
            glow_col
        )

        # ---------------------------------------------------------
        # AMBIENT GLOW
        # ---------------------------------------------------------

        self._draw_ambient(
            bg_accent,
            breath
        )

        # ---------------------------------------------------------
        # ROTATING DISKS
        # ---------------------------------------------------------

        self._draw_rotational_disks(
            main_col,
            glow_col,
            breath
        )

        # ---------------------------------------------------------
        # STATE EFFECT
        # ---------------------------------------------------------

        self._draw_state_visuals(
            main_col,
            glow_col,
            breath,
            t
        )

        # ---------------------------------------------------------
        # CENTRAL CORE
        # ---------------------------------------------------------

        self._draw_retro_core(
            main_col,
            glow_col,
            breath
        )

        # ---------------------------------------------------------
        # TECH READOUTS
        # ---------------------------------------------------------

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

        self.canvas.create_text(

            self.cx,
            305,

            text=f"[ {self.state.upper()} ]",

            fill="#507070",

            font=(
                "Courier New",
                9,
                "bold"
            )
        )

        # ---------------------------------------------------------
        # STATUS BAR
        # ---------------------------------------------------------

        self.canvas.create_text(

            self.cx,
            330,

            text="SYS: ONLINE  //  CORE: STABLE",

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

        # subtle CRT grid

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

        # center axis

        self.canvas.create_line(

            self.cx - 150,
            self.cy,

            self.cx + 150,
            self.cy,

            fill="#062027"
        )

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

        # Very subtle horizontal CRT lines

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

        # Moving scan bar

        scan_y = (
            self.time_step * 28
        ) % 360

        self.canvas.create_line(

            0,
            scan_y,
            360,
            scan_y,

            fill="#073b3f"
        )

    # =============================================================
    # RADAR SWEEP
    # =============================================================

    def _draw_radar(
        self,
        color
    ):

        r = 125

        start = (
            self.angle_radar
        )

        # Tkinter angles work opposite
        # from standard math angles

        self.canvas.create_arc(

            self.cx - r,
            self.cy - r,

            self.cx + r,
            self.cy + r,

            start=start,
            extent=18,

            outline=color,

            style="arc",

            width=2
        )

        # Radar center line

        x, y = self.polar(
            r,
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
    # AMBIENT RINGS
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
        # INNER ROTATING RING
        # ---------------------------------------------------------

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

            width=2
        )

        self.canvas.create_arc(

            self.cx - r3,
            self.cy - r3,

            self.cx + r3,
            self.cy + r3,

            start=(
                self.angle_fast * 1.5
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

        # ---------------------------------------------------------
        # OUTER CORE
        # ---------------------------------------------------------

        core_r = (
            31
            + breath * 5
        )

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
        # INNER TECH RING
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

            start=self.angle_fast + 180,

            extent=100,

            outline=glow_col,

            width=2
        )

        # ---------------------------------------------------------
        # CENTRAL CRT CORE
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
                ) % 2

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

            # Retro orbiting data nodes

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

                amp = (
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
                    42 + amp,
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

                self.canvas.create_line(

                    self.cx - 60,
                    gy,

                    self.cx + 60,
                    gy,

                    fill=main_col,

                    width=1
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

        # Left side

        left_data = [

            "JRV-01",

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

                font=font
            )

            y += 11

        # Right side

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

        # Tiny hex data

        hex_data = (
            "7A 4F 91 C2 00 FF "
            "A1 09 7D 33 8E"
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

        # Top status

        self.canvas.create_text(

            self.cx,
            52,

            text="STARK INDUSTRIES // SYSTEM 01",

            fill=main_col,

            font=(
                "Courier New",
                7,
                "bold"
            )
        )

    # =============================================================
    # ANIMATION
    # =============================================================

    def animate(self):

        self.angle_fast = (
            self.angle_fast + 2.5
        ) % 360

        self.angle_slow = (
            self.angle_slow + 0.8
        ) % 360

        self.angle_radar = (
            self.angle_radar + 1.2
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


if __name__ == "__main__":

    app = JarvisUI()

    app.run()
