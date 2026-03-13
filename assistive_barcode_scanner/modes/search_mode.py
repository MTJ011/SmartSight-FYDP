from services.barcode_service import detect_barcode
from services.voice_service import speak
import time

last_prompt = 0
frame_count = 0
SCAN_EVERY_N_FRAMES = 10  # Only decode every 10th frame


def run(frame):
    global last_prompt, frame_count

    frame_count += 1

    # Skip frames to reduce lag
    if frame_count % SCAN_EVERY_N_FRAMES != 0:
        return "SEARCH", None

    barcodes = detect_barcode(frame)

    if barcodes:
        return "ALIGNMENT", barcodes[0]

    current_time = time.time()
    if current_time - last_prompt > 4:
        speak("Move camera slowly around the product")
        last_prompt = current_time

    return "SEARCH", None