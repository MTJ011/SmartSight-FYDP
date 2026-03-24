import time
from services.voice_service import speak
from services.voice_command_service import get_command

prompts = [
    "Rotate the object slowly",
    "Turn the product around",
    "Tilt the object upward",
    "Tilt the object downward"
]

prompt_index = 0


def wait_for_confirmation():
    while True:
        time.sleep(5)

        speak("Have you done it? Say yes or no.")

        # ✅ Give user 3 seconds to respond
        response = None
        start_time = time.time()

        while time.time() - start_time < 3:
            cmd = get_command()

            if cmd:
                response = cmd
                break

            time.sleep(0.2)  # small delay to avoid CPU overuse

        # ✅ PROCESS RESPONSE
        if response == "yes":
            speak("Good. Moving on.")
            return True

        elif response == "no":
            speak("Okay, take your time.")
            continue  # ask again after 5 sec

        else:
            speak("I didn't catch that.")


def run():
    global prompt_index

    # Speak current instruction
    instruction = prompts[prompt_index]
    speak(instruction)

    # Wait for user confirmation loop
    wait_for_confirmation()

    # Move to next instruction
    prompt_index = (prompt_index + 1) % len(prompts)

    return "ROTATION"