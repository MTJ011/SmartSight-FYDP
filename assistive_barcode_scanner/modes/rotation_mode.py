from services.barcode_service import detect_barcode
from services.voice_service import speak
import time

prompts = [
    "Rotate the object slowly",
    "Turn the product around",
    "Tilt the object upward",
    "Tilt the object downward"
]

last_prompt = 0
prompt_index = 0


def run(frame):

    global last_prompt, prompt_index

    barcodes = detect_barcode(frame)

    if barcodes:
        return "ALIGNMENT", barcodes[0]

    current_time = time.time()

    if current_time - last_prompt > 5:
        speak(prompts[prompt_index])
        prompt_index = (prompt_index + 1) % len(prompts)
        last_prompt = current_time

    return "ROTATION", None