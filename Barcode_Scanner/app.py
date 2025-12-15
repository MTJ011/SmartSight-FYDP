import cv2
from pyzxing import BarCodeReader
import requests
import os
import pyttsx3
import sqlite3
import time
import sys


# -------------------------------
# Initialize ZXing Reader
# -------------------------------
reader = BarCodeReader()

# -------------------------------
# FIXED: Better Text-to-Speech initialization
# -------------------------------
def speak(text):
    """Reinitialize engine each time for reliability"""
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"TTS Error: {e}")

last_barcode = None
last_scan_time = 0
last_product_name = None

# -------------------------------
# Initialize Local Price Database
# -------------------------------
def init_db():
    conn = sqlite3.connect("prices.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            brand TEXT,
            category TEXT,
            price INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# DB Helper Functions
# -------------------------------
def get_local_price(barcode):
    conn = sqlite3.connect("prices.db")
    cur = conn.cursor()
    cur.execute("SELECT price, name, category FROM prices WHERE barcode=?", (barcode,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1], row[2]
    return None, None, None

def save_local_price(barcode, name, brand, category, price):
    conn = sqlite3.connect("prices.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO prices (barcode, name, brand, category, price)
        VALUES (?, ?, ?, ?, ?)
    """, (barcode, name, brand, category, price))
    conn.commit()
    conn.close()
    print(f"✅ Price saved: {barcode} - {name} = {price} PKR")

# -------------------------------
# OpenFoodFacts (Food)
# -------------------------------
def get_food_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("status") == 1:
            product = res.get("product", {})
            return (
                product.get("product_name"),
                product.get("categories"),
                product.get("brands"),
                "Food"
            )
    except Exception as e:
        print(f"Error fetching food data: {e}")
    return None, None, None, None

# -------------------------------
# OpenBeautyFacts (Personal Care)
# -------------------------------
def get_beauty_product(barcode):
    url = f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("status") == 1:
            product = res.get("product", {})
            return (
                product.get("product_name"),
                product.get("categories"),
                product.get("brands"),
                "Personal care product"
            )
    except Exception as e:
        print(f"Error fetching beauty data: {e}")
    return None, None, None, None

# -------------------------------
# Process Barcode - WITH PROPER TTS
# -------------------------------
def process_barcode(barcode_data):
    global last_barcode, last_scan_time, last_product_name

    # Validate barcode first
    if not barcode_data.isdigit() or len(barcode_data) not in [8, 12, 13, 14]:
        print("❌ Invalid barcode format")
        speak("Invalid barcode format.")
        return

    current_time = time.time()

    # Debounce valid barcodes only - INCREASED TIME
    if barcode_data == last_barcode and (current_time - last_scan_time) < 5:
        # Silently ignore duplicate scans (no print statement)
        return

    # Update tracking BEFORE processing
    last_barcode = barcode_data
    last_scan_time = current_time

    print(f"\n🔍 Barcode detected: {barcode_data}")
    print("=" * 40)

    # FIRST check local database
    local_price, local_name, local_category = get_local_price(barcode_data)
    
    if local_price is not None and local_name is not None:
        print(f"📦 Found in local database")
        print(f"Product Name: {local_name}")
        print(f"Category: {local_category or 'Not available'}")
        print(f"Price: {local_price} PKR")
        print("=" * 40)
        
        # SPEAK the details
        speak(f"Product Name: {local_name}. Category: {local_category or 'Not available'}. Price {local_price} rupees.")
        return
    
    # If no local price, fetch from online sources
    beauty = get_beauty_product(barcode_data)
    food = get_food_product(barcode_data)

    if beauty[0]:
        name, category, brand, _ = beauty
        product_type = "Personal care product"
    elif food[0]:
        name, category, brand, _ = food
        category_text = (category or "").lower()
        if any(word in category_text for word in ["food", "drink", "beverage", "snack", "meal"]):
            product_type = "Food"
        else:
            product_type = "Non-food item"
    else:
        # Product not found online
        print("❌ Product not found in online databases.")
        
        if local_name:
            print(f"📦 Product name from local DB: {local_name}")
            speak(f"{local_name}. Price not found. Please enter price.")
        else:
            speak("Product detected, but information is not available. Please enter product details.")
            name = input("Enter product name: ").strip()
            if not name:
                name = "Unknown Product"
            brand = input("Enter brand (or press Enter to skip): ").strip()
            category = input("Enter category (or press Enter to skip): ").strip()
            if not category:
                category = "Unknown"
        
        # Ask for price
        try:
            price = int(input("Enter price (PKR): "))
            save_local_price(barcode_data, name, brand, category, price)
            speak("Price saved successfully.")
        except ValueError:
            print("❌ Invalid price entered.")
            speak("Invalid price entered.")
        return

    # Display product info
    print(f"Product Name : {name}")
    print(f"Type         : {product_type}")
    print(f"Category     : {category or 'Not available'}")
    print("=" * 40)

    # SPEAK the product details
    speak(f"{name}. {product_type}. Price not found. Please enter price.")
    
    try:
        price_input = input("Enter price (PKR): ").strip()
        if price_input:
            price = int(price_input)
            save_local_price(barcode_data, name, brand, category, price)
            speak("Price saved successfully.")
        else:
            speak("No price entered. Product added without price.")
    except ValueError:
        print("❌ Invalid price entered. Please enter numbers only.")
        speak("Invalid price entered.")

# -------------------------------
# MENU
# -------------------------------
print("\n" + "=" * 40)
print("    Assistive Barcode Scanner")
print("=" * 40)
print("1. Scan barcode using camera")
print("2. Enter barcode manually")
print("3. View all saved products")
print("4. Exit")
print("=" * 40)

choice = input("Select option (1-4): ").strip()

# -------------------------------
# OPTION 3: View all saved products
# -------------------------------
if choice == "3":
    conn = sqlite3.connect("prices.db")
    cur = conn.cursor()
    cur.execute("SELECT barcode, name, price FROM prices ORDER BY name")
    products = cur.fetchall()
    conn.close()
    
    if products:
        print(f"\n📊 Saved Products ({len(products)}):")
        print("=" * 60)
        for barcode, name, price in products:
            print(f"{barcode} | {name[:40]:40} | {price:6} PKR")
        print("=" * 60)
        
        # SPEAK the summary
        speak(f"You have {len(products)} products saved in the database.")
    else:
        print("No products saved yet.")
        speak("No products saved yet.")
    sys.exit(0)

# -------------------------------
# OPTION 4: Exit
# -------------------------------
elif choice == "4":
    speak("Goodbye")
    sys.exit(0)

# -------------------------------
# CAMERA MODE
# -------------------------------
elif choice == "1":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access camera")
        speak("Cannot access camera.")
        sys.exit(1)
        
    speak("Camera mode activated. Point the barcode towards the camera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imwrite("frame.png", frame)
        results = reader.decode("frame.png")

        if os.path.exists("frame.png"):
            os.remove("frame.png")

        if results:
            for r in results:
                barcode_data = r.raw if hasattr(r, "raw") else r.get("raw")
                if isinstance(barcode_data, bytes):
                    barcode_data = barcode_data.decode("utf-8")
                if barcode_data:
                    # This will speak on EVERY scan
                    process_barcode(barcode_data)

        cv2.imshow("Assistive Barcode Scanner (Press Q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            speak("Exiting camera mode.")
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------------------
# MANUAL MODE
# -------------------------------
elif choice == "2":
    speak("Manual barcode entry selected.")
    while True:
        barcode = input("\nEnter barcode (or type 'exit'): ").strip()
        if barcode.lower() == 'exit':
            speak("Exiting manual mode.")
            break
        # This will speak on EVERY entry
        process_barcode(barcode)

else:
    speak("Invalid option selected.")