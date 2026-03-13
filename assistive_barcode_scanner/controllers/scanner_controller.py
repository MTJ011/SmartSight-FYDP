import cv2
import time

from services.camera_service import open_camera
from modes import search_mode, rotation_mode, alignment_mode, scan_mode

current_mode = "SEARCH"
last_detection_time = time.time()
detected_barcode = None


def start_scanner():
    global current_mode, last_detection_time, detected_barcode  # ← was missing detected_barcode

    cap = open_camera()
    print("Scanner started")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if current_mode == "SEARCH":
            next_mode, barcode = search_mode.run(frame)

            if barcode:
                last_detection_time = time.time()

            if next_mode == "SEARCH" and time.time() - last_detection_time > 8:
                current_mode = "ROTATION"
            else:
                current_mode = next_mode

        elif current_mode == "ROTATION":
            next_mode, barcode = rotation_mode.run(frame)
            if barcode:
                current_mode = next_mode

        elif current_mode == "ALIGNMENT":
            next_mode, barcode = alignment_mode.run(frame)

            if next_mode == "SCAN":
                current_mode = "SCAN"
                detected_barcode = barcode  # ← now actually saves due to global fix
            else:
                current_mode = next_mode

        elif current_mode == "SCAN":
            next_mode, _ = scan_mode.run(detected_barcode)  # ← passes barcode, not frame
            current_mode = next_mode

        # Show mode on screen
        cv2.putText(frame, f"Mode: {current_mode}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Assistive Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()