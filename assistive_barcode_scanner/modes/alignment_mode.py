from services.barcode_service import detect_barcode
from services.voice_service import speak
import time

stable_count = 0
last_prompt = 0


def run(frame):

    global stable_count, last_prompt

    barcodes = detect_barcode(frame)

    if not barcodes:
        return "SEARCH", None

    barcode = barcodes[0]

    stable_count += 1

    current_time = time.time()

    if current_time - last_prompt > 3:
        speak("Hold steady")
        last_prompt = current_time

    if stable_count > 5:
        stable_count = 0
        return "SCAN", barcode

    return "ALIGNMENT", None