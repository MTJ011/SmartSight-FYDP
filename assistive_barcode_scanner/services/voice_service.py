import pyttsx3
import threading

_lock = threading.Lock()

def speak(text):
    print(f"🔊 {text}")

    def _speak():
        with _lock:  # ← prevents "run loop already started" error
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 160)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")

    threading.Thread(target=_speak, daemon=True).start()