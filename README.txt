# JARVIS RETRO HUD

## Folder structure

JARVIS/
├── main.py
├── jarvis_ui.py
├── jarvis_voice.py
├── jarvis_sounds.py
├── config.py
└── jarvis_sounds/

## Run

Open the JARVIS folder in VS Code and run:

python main.py

## Controls

1 = Sleeping
2 = Waking / Boot
3 = Listening
4 = Processing
5 = Speaking / Greeting
6 = Success
7 = Error
Esc = Exit

## Dependencies

Install these if needed:

pip install pygame pyttsx3

Tkinter is normally included with the Windows Python installation.

## Performance changes

- Animation reduced from ~60 FPS to ~40 FPS.
- WAV files are generated only when missing.
- Sounds are loaded once and reused.
- Voice engine is initialized lazily in a background thread.
- Boot hex data is generated once instead of every frame.
- UI appears before the voice engine has to initialize.
