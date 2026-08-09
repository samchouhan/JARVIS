#UI interface for Jarvis
import tkinter as tk
import math


class JarvisUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("JARVIS")

        # Window size
        width = 350
        height = 350

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = screen_width - width - 30
        y = screen_height - height - 70

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Always stay on top
        self.root.attributes("-topmost", True)

        # Remove Windows title bar
        self.root.overrideredirect(True)

        # Dark background
        self.root.configure(bg="#05070a")

        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="#05070a",
            highlightthickness=0
        )

        self.canvas.pack()

        # Initial state
        self.state = "sleeping"

        # Animation variables
        self.angle = 0
        self.pulse = 0

        # Start animation
        self.animate()

    # -----------------------------------
    # Change Jarvis state
    # -----------------------------------

    def set_state(self, state):

        self.state = state

    # -----------------------------------
    # Draw AI Core
    # -----------------------------------

    def draw_core(self):

        self.canvas.delete("all")

        # Colors
        if self.state == "sleeping":

            main_color = "#00aaff"
            glow_color = "#0066ff"

        else:

            main_color = "#ff7b00"
            glow_color = "#ff3c00"

        # Center of core
        cx = 175
        cy = 145

        # Pulsating effect
        pulse = math.sin(self.pulse) * 8

        # --------------------------------
        # Outer glow
        # --------------------------------

        for i in range(6):

            radius = 105 - i * 10 + pulse

            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline=glow_color,
                width=3
            )

        # --------------------------------
        # Rotating ring 1
        # --------------------------------

        self.canvas.create_arc(
            cx - 80,
            cy - 80,
            cx + 80,
            cy + 80,
            start=self.angle,
            extent=100,
            outline=main_color,
            width=5
        )

        # --------------------------------
        # Rotating ring 2
        # --------------------------------

        self.canvas.create_arc(
            cx - 70,
            cy - 70,
            cx + 70,
            cy + 70,
            start=-self.angle,
            extent=80,
            outline=main_color,
            width=3
        )

        # --------------------------------
        # Rotating ring 3
        # --------------------------------

        self.canvas.create_arc(
            cx - 55,
            cy - 55,
            cx + 55,
            cy + 55,
            start=self.angle * 2,
            extent=120,
            outline=main_color,
            width=2
        )

        # --------------------------------
        # Inner reactor
        # --------------------------------

        radius = 42 + pulse / 3

        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill="#05070a",
            outline=main_color,
            width=4
        )

        # --------------------------------
        # Inner energy
        # --------------------------------

        inner_radius = 25 + pulse / 4

        self.canvas.create_oval(
            cx - inner_radius,
            cy - inner_radius,
            cx + inner_radius,
            cy + inner_radius,
            fill=main_color,
            outline=main_color
        )

        # --------------------------------
        # Core center
        # --------------------------------

        self.canvas.create_oval(
            cx - 10,
            cy - 10,
            cx + 10,
            cy + 10,
            fill="#ffffff",
            outline=""
        )

        # --------------------------------
        # JARVIS text
        # --------------------------------

        self.canvas.create_text(
            175,
            250,
            text="J A R V I S",
            fill=main_color,
            font=("Arial", 18, "bold")
        )

        # --------------------------------
        # Status
        # --------------------------------

        if self.state == "sleeping":

            status = "SLEEPING"

        elif self.state == "listening":

            status = "LISTENING"

        elif self.state == "processing":

            status = "PROCESSING"

        else:

            status = self.state.upper()

        self.canvas.create_text(
            175,
            280,
            text=status,
            fill="#aaaaaa",
            font=("Arial", 10)
        )

    # -----------------------------------
    # Animation
    # -----------------------------------

    def animate(self):

        self.angle += 3

        self.pulse += 0.15

        self.draw_core()

        self.root.after(30, self.animate)

    # -----------------------------------
    # Run GUI
    # -----------------------------------

    def run(self):

        self.root.mainloop()


# ---------------------------------------
# TEST THE UI
# ---------------------------------------

if __name__ == "__main__":

    jarvis = JarvisUI()

    jarvis.run()
