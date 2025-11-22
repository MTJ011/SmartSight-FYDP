import cv2
from pyzxing import BarCodeReader
import requests
import os

# Initialize ZXing Reader
reader = BarCodeReader()

# Fetch product info from OpenFoodFacts API
def get_product_from_api(barcode):
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("code") == "OK" and res.get("total") > 0:
            item = res["items"][0]
            name = item.get("title")
            price = item.get("lowest_recorded_price") or item.get("highest_recorded_price")
            category = item.get("category")
            return name, price, category
    except:
        pass
    
    return None, None, None


cap = cv2.VideoCapture(0)
print("Scanning barcodes… Press q to quit.")
print("Point at REAL product barcodes (12-13 digits)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Save frame temporarily
    cv2.imwrite("frame.png", frame)
    results = reader.decode("frame.png")

    # Delete the temporary image
    if os.path.exists("frame.png"):
        os.remove("frame.png")

    if results:
        for r in results:

            # Extract raw barcode data
            if hasattr(r, "raw"):
                barcode_data = r.raw
            elif isinstance(r, dict):
                barcode_data = r.get("raw")
            else:
                continue

            # Convert bytes → string
            if isinstance(barcode_data, bytes):
                barcode_data = barcode_data.decode("utf-8")

            # Only accept EAN-13 / UPC-A
            if barcode_data and barcode_data.isdigit():
                if len(barcode_data) in [12, 13]:

                    print(f"Valid barcode detected: {barcode_data}")
                    
                    name, price, category = get_product_from_api(barcode_data)
                    text = f"{barcode_data}"
                    
                    if name:
                        print("\n==============================")
                        print(f"Product Name : {name}")
                        print(f"Price        : {price} PKR" if price else "Price        : Not available")
                        print(f"Category     : {category}" if category else "Category     : Not available")
                        print("==============================\n")
                    
                        text += f" | {name}"
                    else:
                        print(f"❌ Product not found: {barcode_data}")
                        text += " | Not found"

                        print(f"✅ PRODUCT FOUND: {name}")

                    # Show text on camera feed
                    cv2.putText(
                        frame, text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2
                    )

                else:
                    print(f"Ignoring invalid format: {barcode_data} (length: {len(barcode_data)})")

    cv2.imshow("ZXing Scanner - Point at REAL barcodes", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
