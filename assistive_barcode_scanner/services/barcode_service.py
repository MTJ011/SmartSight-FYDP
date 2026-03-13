from pyzxing import BarCodeReader
import cv2
import os
import tempfile

reader = BarCodeReader()


def detect_barcode(frame):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    cv2.imwrite(tmp_path, frame)
    detected_codes = []

    try:
        results = reader.decode(tmp_path)

        if results:
            for r in results:
                if isinstance(r, dict):
                    barcode_data = r.get("parsed") or r.get("raw")
                else:
                    barcode_data = getattr(r, "parsed", None) or getattr(r, "raw", None)

                if isinstance(barcode_data, bytes):
                    barcode_data = barcode_data.decode("utf-8")

                if not barcode_data:
                    continue

                detected_codes.append(barcode_data)

                # Draw bounding box
                points = r.get("points") if isinstance(r, dict) else getattr(r, "points", None)
                if points:
                    pts = [(int(p[0]), int(p[1])) for p in points]
                    for i in range(len(pts)):
                        cv2.line(frame, pts[i], pts[(i + 1) % len(pts)], (0, 255, 0), 2)
                    cv2.putText(frame, barcode_data, pts[0],
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return detected_codes