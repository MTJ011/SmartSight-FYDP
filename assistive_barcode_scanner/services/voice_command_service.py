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

    # ✅ YES / NO (enhanced)
    "yes": [
        "yes", "yeah", "yep", "done", "okay", "ok",
        "i did", "completed", "haan", "han"
    ],
    "no": [
        "no", "not yet", "wait", "hold on",
        "nahi", "nope"
    ]
}


def get_command():
    global _current_command
    with _lock:
        cmd = _current_command
        _current_command = None
    return cmd


def _match_command(text):
    """
    Match spoken text against command triggers.
    Supports both single words and phrases.
    """
    words = text.split()

    for cmd, triggers in COMMANDS.items():
        for trigger in triggers:
            trigger_words = trigger.split()

            # ✅ Exact phrase match (for multi-word triggers)
            if trigger in text:
                return cmd

            # ✅ Word-level match (safe)
            if len(trigger_words) == 1 and trigger in words:
                return cmd

    return None


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

            cmd = _match_command(text)

            if cmd:
                with _lock:
                    _current_command = cmd
                print(f"✅ Command: {cmd}")

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio")
        except Exception as e:
            print(f"Voice error: {e}")


def start_listening():
    threading.Thread(target=_listen_loop, daemon=True).start()