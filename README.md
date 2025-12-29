## QR Code Generator (macOS GUI)

Simple macOS GUI QR generator that supports:
- **URL**: enter a URL and generate a QR code
- **E-mail**: generates a `mailto:` QR from e-mail (required) + optional subject/body

### Setup

```bash
cd /Users/rob/Unicorn/dev/qr
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Run

```bash
python app.py
```

This will open a native window. Use the **Quit** button to exit.

### (Optional) Web version

If you want the previous browser-based version, it’s preserved as:

```bash
python -m pip install Flask==3.1.0
python web_app.py
```

Then open `http://127.0.0.1:8000`.




