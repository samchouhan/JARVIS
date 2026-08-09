#This is alternate Jarvis UI design
import math
import random
import time
import pygame

# --- CONFIG & COLORS ---
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)

CYAN = (0, 240, 255)
BLUE = (0, 100, 255)
AMBER = (255, 170, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
PURPLE = (180, 50, 255)
WHITE = (240, 250, 255)


class JarvisHUD:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("JARVIS Phase 3 - Smooth Core & Rotating Disks")
        self.clock = pygame.time.Clock()
        self.running = True

        # State Tracking
        self.state = "sleeping"
        self.state_time = time.time()

        # Shared Visual Parameters
        self.target_color = BLUE
        self.current_color = list(BLUE)

        # Disk Angles
        self.disk1_angle = 0.0
        self.disk2_angle = 0.0

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_time = time.time()

            color_map = {
                "sleeping": (10, 80, 200),
                "waking": CYAN,
                "listening": CYAN,
                "thinking": PURPLE,
                "speaking": AMBER,
                "success": GREEN,
                "error": RED,
            }
            self.target_color = color_map.get(new_state, CYAN)

    def update_colors(self):
        # Smooth asymptotic RGB transition across state switches
        for i in range(3):
            self.current_color[i] += (self.target_color[i] - self.current_color[i]) * 0.04
        return tuple(map(int, self.current_color))

    # --- ROTATING MECHANICAL DISKS ---
    def draw_rotating_disks(self, color, t):
        # Update angles (disk 1 clockwise, disk 2 counter-clockwise)
        self.disk1_angle += 0.012
        self.disk2_angle -= 0.008

        # --- DISK 1: Inner Tech Ring (Radius 190) ---
        r1 = 190
        pygame.draw.circle(self.screen, (color[0] // 3, color[1] // 3, color[2] // 3), CENTER, r1, 1)
        num_ticks = 24
        for i in range(num_ticks):
            angle = self.disk1_angle + (i * (math.tau / num_ticks))
            inner_pt = (CENTER[0] + math.cos(angle) * (r1 - 6), CENTER[1] + math.sin(angle) * (r1 - 6))
            outer_pt = (CENTER[0] + math.cos(angle) * (r1 + 6), CENTER[1] + math.sin(angle) * (r1 + 6))
            pygame.draw.line(self.screen, color, inner_pt, outer_pt, 2 if i % 4 == 0 else 1)

        # --- DISK 2: Outer Segmented HUD Ring (Radius 220) ---
        r2 = 220
        num_arcs = 4
        arc_len = math.radians(50)
        for i in range(num_arcs):
            start_angle = self.disk2_angle + (i * (math.tau / num_arcs))
            # Draw segmented arc blocks
            rect = pygame.Rect(CENTER[0] - r2, CENTER[1] - r2, r2 * 2, r2 * 2)
            pygame.draw.arc(self.screen, color, rect, start_angle, start_angle + arc_len, 3)

    # --- DRAW ROUTER ---
    def draw_core(self):
        self.screen.fill((4, 6, 12))
        color = self.update_colors()
        t = time.time() - self.state_time

        # Base HUD framework & dynamic disks
        self.draw_base_rings(color)
        self.draw_rotating_disks(color, time.time())

        # State animations
        if self.state == "sleeping":
            self.draw_sleeping(color, t)
        elif self.state == "waking":
            self.draw_waking(color, t)
        elif self.state == "listening":
            self.draw_listening(color, t)
        elif self.state == "thinking":
            self.draw_thinking(color, t)
        elif self.state == "speaking":
            self.draw_speaking(color, t)
        elif self.state == "success":
            self.draw_success(color, t)
        elif self.state == "error":
            self.draw_error(color, t)

    def draw_base_rings(self, color):
        pygame.draw.circle(self.screen, (color[0] // 8, color[1] // 8, color[2] // 8), CENTER, 160)
        pygame.draw.circle(self.screen, color, CENTER, 160, 1)

    # --- SMOOTH BREATHING & ANIMATIONS ---
    def draw_sleeping(self, color, t):
        """Smoothed organic breathing cycle using an exponential sine ease."""
        # Exponential sine produces a slow lingering resting phase and a smooth peak
        raw_breath = (math.exp(math.sin(t * 1.5)) - 0.36787944) / 2.35040238
        
        radius = int(32 + raw_breath * 22)
        glow_alpha = int(30 + raw_breath * 100)

        # Multi-layer breathing glow
        glow_color = (
            (color[0] * glow_alpha) // 255,
            (color[1] * glow_alpha) // 255,
            (color[2] * glow_alpha) // 255,
        )

        pygame.draw.circle(self.screen, glow_color, CENTER, radius + 15)
        pygame.draw.circle(self.screen, color, CENTER, radius, 2)
        pygame.draw.circle(self.screen, WHITE, CENTER, max(1, int(radius * 0.3)))

    def draw_waking(self, color, t):
        progress = min(1.0, t / 1.2)
        radius = int(10 + progress * 75)

        pygame.draw.circle(self.screen, WHITE, CENTER, int(radius * 0.5))
        pygame.draw.circle(self.screen, color, CENTER, radius, 3)

        if random.random() > 0.2:
            angle = random.uniform(0, math.tau)
            arc_end = (CENTER[0] + math.cos(angle) * (radius + 30), CENTER[1] + math.sin(angle) * (radius + 30))
            pygame.draw.line(self.screen, WHITE, CENTER, arc_end, 2)

        if progress >= 1.0:
            self.set_state("listening")

    def draw_listening(self, color, t):
        pygame.draw.circle(self.screen, WHITE, CENTER, 30)
        for i in range(3):
            wave_t = (t * 1.8 + i * 0.7) % 2.2
            wave_r = int(35 + wave_t * 55)
            alpha_scale = max(0.0, 1.0 - (wave_t / 2.2))
            wave_color = (int(color[0] * alpha_scale), int(color[1] * alpha_scale), int(color[2] * alpha_scale))
            pygame.draw.circle(self.screen, wave_color, CENTER, wave_r, 2)

    def draw_thinking(self, color, t):
        for i in range(3):
            speed = (i + 1) * 2.5
            angle = t * speed
            r = 45 + i * 22
            x = CENTER[0] + math.cos(angle) * r
            y = CENTER[1] + math.sin(angle) * r
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), 4)
            pygame.draw.circle(self.screen, color, CENTER, r, 1)

        pygame.draw.circle(self.screen, color, CENTER, 22)

    def draw_speaking(self, color, t):
        amp = abs(math.sin(t * 7.0) * math.cos(t * 2.5)) * 35
        core_r = int(35 + amp * 0.4)

        pygame.draw.circle(self.screen, color, CENTER, core_r)
        pygame.draw.circle(self.screen, WHITE, CENTER, int(core_r * 0.6))

        segments = 32
        for i in range(segments):
            angle = (i / segments) * math.tau
            h = abs(math.sin(t * 8 + i)) * amp
            p1 = (CENTER[0] + math.cos(angle) * 110, CENTER[1] + math.sin(angle) * 110)
            p2 = (CENTER[0] + math.cos(angle) * (110 + h), CENTER[1] + math.sin(angle) * (110 + h))
            pygame.draw.line(self.screen, color, p1, p2, 2)

    def draw_success(self, color, t):
        burst_r = int(30 + (t * 180) % 220)
        pygame.draw.circle(self.screen, color, CENTER, burst_r, 3)
        pygame.draw.circle(self.screen, GREEN, CENTER, 40)
        pygame.draw.circle(self.screen, WHITE, CENTER, 20)

    def draw_error(self, color, t):
        jitter = (random.randint(-3, 3), random.randint(-3, 3))
        err_center = (CENTER[0] + jitter[0], CENTER[1] + jitter[1])

        pygame.draw.circle(self.screen, RED, err_center, 40)
        pygame.draw.line(self.screen, WHITE, (err_center[0] - 25, err_center[1]), (err_center[0] + 25, err_center[1]), 3)

        for _ in range(4):
            gy = err_center[1] + random.randint(-80, 80)
            pygame.draw.line(self.screen, RED, (err_center[0] - 120, gy), (err_center[0] + 120, gy), 1)

    def run(self):
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    keys = {
                        pygame.K_1: "sleeping",
                        pygame.K_2: "waking",
                        pygame.K_3: "listening",
                        pygame.K_4: "thinking",
                        pygame.K_5: "speaking",
                        pygame.K_6: "success",
                        pygame.K_7: "error",
                    }
                    if event.key in keys:
                        self.set_state(keys[event.key])

            self.draw_core()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    app = JarvisHUD()
    app.run()
