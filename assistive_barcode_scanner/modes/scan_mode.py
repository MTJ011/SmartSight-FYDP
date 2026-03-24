from services.voice_service import speak


def run(barcode):
    speak("Barcode detected. Hold still.")
    
    # TODO: fetch product info here
    result = f"Product code is {barcode}"
    speak(result)

    return result