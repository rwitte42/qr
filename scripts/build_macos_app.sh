#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "Missing .venv/. Create it first: python3 -m venv .venv" >&2
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

python -m pip install -U pip
python -m pip install -U pyinstaller

# Optional configuration (env vars):
# - QR_BUNDLE_ID: bundle identifier (default: com.rwitte42.qr)
# - QR_ICON_ICNS: path to a .icns file (optional)
# - QR_APP_VERSION: short version string (optional, e.g. 1.0.0)
APP_NAME="QR Code Generator"
BUNDLE_ID="${QR_BUNDLE_ID:-com.rwitte42.qr}"
ICON_ICNS="${QR_ICON_ICNS:-}"
APP_VERSION="${QR_APP_VERSION:-}"

ICON_ARGS=()
if [[ -n "$ICON_ICNS" ]]; then
  if [[ ! -f "$ICON_ICNS" ]]; then
    echo "QR_ICON_ICNS was set but file not found: $ICON_ICNS" >&2
    exit 1
  fi
  ICON_ARGS+=(--icon "$ICON_ICNS")
fi

# Build a double-clickable macOS app bundle.
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --osx-bundle-identifier "$BUNDLE_ID" \
  "${ICON_ARGS[@]}" \
  app.py

APP_PATH="$ROOT_DIR/dist/$APP_NAME.app"
PLIST="$APP_PATH/Contents/Info.plist"

if [[ -n "$APP_VERSION" && -f "$PLIST" ]]; then
  /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $APP_VERSION" "$PLIST" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $APP_VERSION" "$PLIST"
  /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $APP_VERSION" "$PLIST" 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $APP_VERSION" "$PLIST"
fi

echo
echo "Built app:"
echo "  $APP_PATH"
echo
echo "Bundle ID:"
echo "  $BUNDLE_ID"
if [[ -n "$APP_VERSION" ]]; then
  echo
  echo "Version:"
  echo "  $APP_VERSION"
fi


