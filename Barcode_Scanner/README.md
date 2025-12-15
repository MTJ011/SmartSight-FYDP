# SmartSight Barcode Scanner

A Python-based barcode scanner application that uses computer vision to detect barcodes from a camera feed, fetches product information from online databases (OpenFoodFacts and OpenBeautyFacts), and provides text-to-speech feedback. It also maintains a local SQLite database for storing product prices and details.

## Features

- Real-time barcode detection using ZXing (via pyzxing)
- Product information retrieval from OpenFoodFacts (food) and OpenBeautyFacts (personal care)
- Local SQLite database for storing custom product prices and details
- Text-to-speech announcements for detected products
- Debouncing to prevent repeated announcements for the same barcode
- Support for various barcode lengths (8, 12, 13, 14 digits)

## Installation

### Prerequisites

- Python 3.8 or higher
- A camera (webcam) connected to your computer

### Install Dependencies

Run the following command to install the required Python packages:

```bash
pip install opencv-python pyzxing requests pyttsx3
```

### Additional Setup

- **pyttsx3**: On Windows, it uses SAPI5. Ensure your system's text-to-speech engine is configured.
- **Camera Access**: The app uses OpenCV to access the default camera (index 0). Make sure your camera is enabled and not in use by other applications.

## Usage

1. Clone or download the repository.
2. Navigate to the project directory.
3. Run the application:

```bash
python app.py
```

4. Point your camera at a barcode. The app will:
   - Detect and validate the barcode.
   - Check the local database for stored information.
   - If not found locally, query online databases.
   - Announce the product details via text-to-speech.
   - Prompt for price input if not available, and save it to the local database.

5. Press 'q' to quit the application.

### Local Database

- The app creates a `prices.db` SQLite database to store product information.
- You can reset the database by running `python reset_prices.py` (if available).

## File Structure

- `app.py`: Main application script.
- `prices.db`: Local SQLite database (auto-created).
- `reset_prices.py`: Script to reset the local database (optional).
- `README.md`: This file.

## Contributing

Feel free to fork the repository and submit pull requests for improvements.

## License

This project is open-source. Please check the repository for license details.