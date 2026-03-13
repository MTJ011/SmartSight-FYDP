import time
from services.database_service import get_local_price, save_local_price
from services.product_service import get_food_product, get_beauty_product
from services.voice_service import speak

last_barcode = None
last_scan_time = 0


def process_barcode(barcode):

    global last_barcode, last_scan_time

    if not barcode.isdigit() or len(barcode) not in [8, 12, 13, 14]:
        print("Invalid barcode format")
        return

    current_time = time.time()

    if barcode == last_barcode and (current_time - last_scan_time) < 5:
        return

    last_barcode = barcode
    last_scan_time = current_time

    print(f"\nBarcode detected: {barcode}")

    # ── CHECK LOCAL DATABASE FIRST ────────────────────────────────
    local_price, local_name, local_category = get_local_price(barcode)

    if local_price is not None:
        print(f"✅ Found in local DB: {local_name} — {local_price} PKR")
        speak(f"{local_name}. Price {local_price} rupees.")
        return

    # ── CHECK ONLINE APIs ─────────────────────────────────────────
    beauty = get_beauty_product(barcode)
    food = get_food_product(barcode)

    if beauty[0]:
        name, category, brand, _ = beauty
        print(f"✅ Found online (beauty): {name}")

    elif food[0]:
        name, category, brand, _ = food
        print(f"✅ Found online (food): {name}")

    else:
        # ── NOT FOUND ANYWHERE — ASK USER ────────────────────────
        print("\n⚠️  Product not found online or locally.")
        speak("Product not found. Please enter details.")

        name = input("Enter product name: ").strip()
        category = input("Enter category: ").strip()
        brand = input("Enter brand (or press Enter to skip): ").strip()

        while True:
            try:
                price = float(input("Enter price in PKR: ").strip())
                break
            except ValueError:
                print("❌ Invalid price. Please enter a number.")

        save_local_price(barcode, name, brand, category, price)
        print(f"✅ Saved: {name} — {price} PKR")
        speak(f"{name} saved. Price {price} rupees.")
        return

    # ── PRODUCT FOUND ONLINE — ASK PRICE ONLY ────────────────────
    print(f"   Name    : {name}")
    print(f"   Category: {category}")
    print(f"   Brand   : {brand}")
    speak(f"Found {name}.")

    while True:
        try:
            price = float(input("Enter local price in PKR: ").strip())
            break
        except ValueError:
            print("❌ Invalid price. Please enter a number.")

    save_local_price(barcode, name, brand, category, price)
    print(f"✅ Price saved: {name} — {price} PKR")
    speak(f"{name}. Price {price} rupees.")