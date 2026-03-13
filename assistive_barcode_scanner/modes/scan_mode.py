from services.scan_service import process_barcode

def run(barcode):
    if barcode:
        process_barcode(barcode)
    return "SEARCH", None