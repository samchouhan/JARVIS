# ================================================================
# JARVIS CONFIGURATION
# ================================================================

WINDOW_WIDTH = 360
WINDOW_HEIGHT = 360

BACKGROUND = "#020b0d"

# ~40 FPS. Lower CPU usage than 16ms / ~60 FPS.
FRAME_DELAY = 25

BOOT_DURATION = 5.0

VOICE_RATE = 145
VOICE_VOLUME = 1.0

SOUND_PATH = "jarvis_sounds"

BOOT_MODULES = [
    ("POWER CORE", 0.12),
    ("MEMORY ARRAY", 0.25),
    ("NEURAL NETWORK", 0.40),
    ("VOICE MODULE", 0.55),
    ("SENSOR ARRAY", 0.70),
    ("SECURITY SYSTEM", 0.84),
    ("JARVIS CORE", 1.00),
]

PALETTES = {
    "sleeping": ("#0088aa", "#005577", "#032025"),
    "waking": ("#00ffff", "#008888", "#063333"),
    "listening": ("#00ffcc", "#008877", "#00332c"),
    "processing": ("#c084ff", "#673b88", "#251536"),
    "speaking": ("#ffb000", "#996600", "#332000"),
    "success": ("#00ff66", "#008833", "#002211"),
    "error": ("#ff3344", "#881122", "#33070c"),
}

KEY_STATE_MAP = {
    "1": "sleeping",
    "2": "waking",
    "3": "listening",
    "4": "processing",
    "5": "speaking",
    "6": "success",
    "7": "error",
}
