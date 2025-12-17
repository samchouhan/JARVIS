"""
Improved Jarvis-style Voice Assistant (Beginner → Intermediate)
Features:
- Wake word ("jarvis")
- Command confirmation
- Retry limit
- Help command
- Command logging
- Clean shutdown
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import pywhatkit
import sys
import time

# ---------------- CONFIG ----------------
WAKE_WORD = "jarvis"
LANG = "en"
VOICE_RATE = 150
VOICE_VOLUME = 1.0
NOTES_FILE = "notes.txt"
LOG_FILE = "command_log.txt"
MAX_RETRIES = 2
# ----------------------------------------

recognizer = sr.Recognizer()
tts = pyttsx3.init()
tts.setProperty("rate", VOICE_RATE)
tts.setProperty("volume", VOICE_VOLUME)

voices = tts.getProperty("voices")
if voices:
    tts.setProperty("voice", voices[0].id)

# -------------- CORE UTILS ----------------

def speak(text):
    print("Jarvis:", text)
    tts.say(text)
    tts.runAndWait()

def log_command(cmd):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {cmd}\n")

def listen(timeout=None, phrase_time_limit=None):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return None
    try:
        return recognizer.recognize_google(audio, language=LANG).lower()
    except:
        return None

# -------------- COMMANDS ------------------

def tell_time():
    speak(datetime.datetime.now().strftime("The time is %I:%M %p"))

def tell_date():
    speak(datetime.date.today().strftime("Today's date is %B %d, %Y"))

def open_site(cmd):
    site = cmd.replace("open", "").strip()
    if "youtube" in site:
        webbrowser.open("https://youtube.com")
    elif "google" in site:
        webbrowser.open("https://google.com")
    else:
        webbrowser.open(f"https://www.google.com/search?q={site}")
    speak(f"Opening {site}")

def wiki_search(query):
    try:
        speak("Searching Wikipedia")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except:
        speak("Wikipedia result not found.")

def play_youtube(query):
    speak(f"Playing {query}")
    pywhatkit.playonyt(query)

def take_note(note):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {note}\n")
    speak("Note saved.")

def show_help():
    speak(
        "I can tell time, date, open websites, search Wikipedia, play YouTube songs, and take notes."
    )

# ----------- COMMAND PARSER ----------------

def parse_command(command):
    log_command(command)

    if "time" in command:
        tell_time()
    elif "date" in command:
        tell_date()
    elif command.startswith("open"):
        open_site(command)
    elif "wikipedia" in command:
        wiki_search(command.replace("wikipedia", "").strip())
    elif command.startswith("play"):
        play_youtube(command.replace("play", "").strip())
    elif "note" in command:
        take_note(command.replace("note", "").strip())
    elif "help" in command:
        show_help()
    elif any(x in command for x in ["exit", "quit", "stop", "bye"]):
        speak("Goodbye.")
        sys.exit(0)
    else:
        speak("I did not understand that command.")

# -------------- MAIN LOOP ------------------

def main():
    speak("Jarvis is online. Say jarvis to wake me.")

    while True:
        text = listen(timeout=5, phrase_time_limit=4)
        if text and WAKE_WORD in text:
            speak("Yes?")
            retries = 0

            while retries < MAX_RETRIES:
                command = listen(timeout=6, phrase_time_limit=8)
                if command:
                    parse_command(command)
                    break
                else:
                    retries += 1
                    speak("I didn't catch that. Please repeat.")

        time.sleep(0.3)

# -------------- ENTRY ---------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Shutting down.")
    except Exception as e:
        print("Error:", e)
        speak("An unexpected error occurred.")
