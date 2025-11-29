"""
Simple Jarvis-style voice assistant (beginner-friendly).
Features: wake-word ("jarvis"), speech recognition, offline TTS, some commands.
Requirements: SpeechRecognition, pyttsx3, wikipedia, pywhatkit, pyaudio (for microphone)
"""
import pyaudio
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import pywhatkit
import os
import sys
import time

# ------------------ Configuration ------------------
WAKE_WORD = "jarvis"   # say "jarvis" to wake it up
VOICE_RATE = 150       # speech speed
VOICE_VOLUME = 1.0     # 0.0 to 1.0
LANG = "en"            # language for speech recognition (if you want to change)
NOTES_FILE = "notes.txt"
# ---------------------------------------------------

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()#Ears of JARVIS
tts = pyttsx3.init()
tts.setProperty("rate", VOICE_RATE)
tts.setProperty("volume", VOICE_VOLUME)

# Optionally change voice (male/female) - platform dependent
voices = tts.getProperty("voices")
if voices:
    # choose a voice index (0 or 1 usually)
    tts.setProperty("voice", voices[0].id)

def speak(text: str):
    """Say text out loud and print to console."""
    print("Jarvis:", text)
    tts.say(text)
    tts.runAndWait()

def listen(timeout=None, phrase_time_limit=None):
    """
    Listen from microphone and return recognized text (or None).
    - timeout: maximum seconds to wait for phrase to start
    - phrase_time_limit: max seconds for phrase duration
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return None
    try:
        # Use Google's free recognizer (requires internet) but often works well.
        # For offline recognition, you'd need to set up VOSK or similar.
        text = recognizer.recognize_google(audio, language=LANG)
        return text.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        # network/system error
        speak("Network error or speech recognition service unavailable.")
        return None

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}")

def tell_date():
    today = datetime.date.today().strftime("%B %d, %Y")
    speak(f"Today's date is {today}")

def open_website(name):
    """Open common websites or accept a full URL."""
    name = name.replace("open ", "").strip()
    # simple mapping
    if "youtube" in name:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    elif "google" in name:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
    elif name.startswith("http"):
        webbrowser.open(name)
        speak("Opening the link.")
    else:
        # try search query
        webbrowser.open(f"https://www.google.com/search?q={name}")
        speak(f"Searching {name} on Google.")

def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except wikipedia.DisambiguationError as e:
        speak("Your query is ambiguous. I will open the wiki page list in your browser.")
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
    except Exception:
        speak("I couldn't find that on Wikipedia.")

def play_on_youtube(query):
    speak(f"Playing {query} on YouTube.")
    pywhatkit.playonyt(query)

def take_note(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} - {text}\n"
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    speak("Note saved.")

def parse_command(command):
    """Handle different commands from the user text."""
    if command is None:
        return

    # Basic commands
    if "time" in command:
        tell_time()
    elif "date" in command:
        tell_date()
    elif command.startswith("open "):
        open_website(command)
    elif command.startswith("search wikipedia for ") or command.startswith("wikipedia "):
        # allow "wikipedia python" or "search wikipedia for python"
        query = command.replace("search wikipedia for ", "").replace("wikipedia ", "").strip()
        search_wikipedia(query)
    elif command.startswith("play "):
        query = command.replace("play ", "").strip()
        play_on_youtube(query)
    elif command.startswith("note ") or command.startswith("take note "):
        note = command.replace("note ", "").replace("take note ", "").strip()
        take_note(note)
    elif "stop" in command or "goodbye" in command or "exit" in command or "quit" in command:
        speak("Goodbye. Shutting down.")
        sys.exit(0)
    else:
        # fallback: search web
        speak("I didn't understand exactly. Should I search the web for that?")
        ans = listen(timeout=5, phrase_time_limit=5)
        if ans and ("yes" in ans or "yeah" in ans or "sure" in ans):
            webbrowser.open(f"https://www.google.com/search?q={command}")
            speak(f"Searching the web for {command}.")
        else:
            speak("Okay, let me know another command.")

def main_loop():
    speak("Jarvis is online. Say 'jarvis' to wake me up.")
    while True:
        print("Listening for wake word...")
        text = listen(timeout=5, phrase_time_limit=4)  # waits for phrase; gives None if timeout
        if text:
            print("You said:", text)
            if WAKE_WORD in text:
                speak("Yes?")
                # after wake word, listen for the real command
                command = listen(timeout=6, phrase_time_limit=10)
                if command:
                    print("Command:", command)
                    parse_command(command)
                else:
                    speak("I didn't hear a command. Say it again.")
            else:
                # optionally react to direct commands without wake-word if you prefer:
                # parse_command(text)
                pass
        # loop continues; feel free to add a small sleep to reduce CPU use
        time.sleep(0.3)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        speak("Shutting down. Bye.")
    except Exception as e:
        # For debugging: print or log the exception
        print("Error:", e)
        speak("An error occurred. Check the console for details.")
