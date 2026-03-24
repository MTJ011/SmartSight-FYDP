import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
_current_command = None
_lock = threading.Lock()

COMMANDS = {
    "scan": ["scan", "start", "begin"],
    "repeat": ["repeat", "again", "what"],
    "stop": ["stop", "pause", "quit"],
    "help": ["help", "how", "instructions"],
}


def get_command():
    global _current_command
    with _lock:
        cmd = _current_command
        _current_command = None
    return cmd


def _listen_loop():
    global _current_command
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)

    print("🎤 Voice commands ready")

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
            text = recognizer.recognize_google(audio).lower().strip()
            print(f"🎤 Heard: '{text}'")

            for cmd, triggers in COMMANDS.items():
                if any(t in text for t in triggers):
                    with _lock:
                        _current_command = cmd
                    print(f"✅ Command: {cmd}")
                    break

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Voice error: {e}")


def start_listening():
    threading.Thread(target=_listen_loop, daemon=True).start()