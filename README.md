## QR Code Generator (macOS GUI)

Simple macOS GUI QR generator that supports:
- **URL**: enter a URL and generate a QR code
- **E-mail**: generates a `mailto:` QR from e-mail (required) + optional subject/body
- **Save PNG…**: save the most recently generated QR to a `.png`
- **Reset**: clears the QR + resets fields (also happens automatically when switching URL/E-mail)

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

### Build a macOS `.app` (double-clickable)

This uses [PyInstaller](https://pyinstaller.org/) to build a local `.app` bundle:

```bash
./scripts/build_macos_app.sh
```

Output:
- `dist/QR Code Generator.app`

Note: the built app is **unsigned**. If macOS Gatekeeper blocks it, right-click → **Open**.

### Bundle ID, icon, signing, notarization (optional)

- **Bundle ID**:

```bash
QR_BUNDLE_ID="com.rwitte42.qr" ./scripts/build_macos_app.sh
```

- **Icon** (provide a `.icns`):

```bash
QR_ICON_ICNS="/absolute/path/to/icon.icns" ./scripts/build_macos_app.sh
```

- **Sign + notarize** (requires Apple Developer account):

```bash
SIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)" \
NOTARY_PROFILE="your-notarytool-profile" \
./scripts/sign_and_notarize_macos_app.sh
```

### (Optional) Web version

If you want the previous browser-based version, it’s preserved as:

```bash
python -m pip install Flask==3.1.0
python web_app.py
```

Then open `http://127.0.0.1:8000`.




