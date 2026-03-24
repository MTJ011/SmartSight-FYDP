import cv2
import time
from services.camera_service import open_camera
from services.voice_service import speak
from services.beep_service import start_beep_loop, stop_beep
from services.voice_command_service import start_listening, get_command
from modes import search_mode, scan_mode

current_mode = "SEARCH"
detected_barcode = None
last_result = None


def start_scanner():
    global current_mode, detected_barcode, last_result

    start_listening()
    start_beep_loop()

    cap = open_camera()

    speak(
        "Assistive barcode scanner ready. "
        "Hold a product in front of you and I will find the barcode. "
        "Say help anytime for instructions."
    )

    print("Scanner started")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ── GLOBAL VOICE COMMANDS ─────────────────────────────────
        cmd = get_command()

        if cmd == "repeat":
            if last_result:
                speak(last_result)
            else:
                speak("No result yet. Hold a product in front of the camera.")

        elif cmd == "scan" and current_mode == "PAUSED":
            current_mode = "SEARCH"
            speak("Scanning resumed.")

        # ── MODE LOGIC ────────────────────────────────────────────
        if current_mode == "SEARCH":
            next_mode, barcode = search_mode.run(frame)
            if barcode:
                detected_barcode = barcode
                current_mode = "SCAN"
            elif next_mode == "PAUSED":
                current_mode = "PAUSED"

        elif current_mode == "SCAN":
            scan_mode.run(detected_barcode)
            current_mode = "SEARCH"
            detected_barcode = None

        elif current_mode == "PAUSED":
            cv2.putText(frame, "PAUSED — say 'Scan' to resume",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 0, 255), 2)

        # ── DISPLAY ───────────────────────────────────────────────
        color = (0, 255, 0) if current_mode == "SCAN" else \
                (0, 0, 255) if current_mode == "PAUSED" else \
                (0, 255, 255)

        cv2.putText(frame, f"Mode: {current_mode}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Assistive Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            stop_beep()
            break

    cap.release()
    cv2.destroyAllWindows()