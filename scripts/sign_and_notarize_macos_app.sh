#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

APP_NAME="${APP_NAME:-QR Code Generator}"
APP_PATH="${APP_PATH:-$ROOT_DIR/dist/$APP_NAME.app}"

# REQUIRED env vars:
# - SIGN_IDENTITY: e.g. "Developer ID Application: Your Name (TEAMID)"
# - NOTARY_PROFILE: name created via: xcrun notarytool store-credentials --keychain-profile ...
SIGN_IDENTITY="${SIGN_IDENTITY:-}"
NOTARY_PROFILE="${NOTARY_PROFILE:-}"

if [[ ! -d "$APP_PATH" ]]; then
  echo "App not found at: $APP_PATH" >&2
  echo "Build it first: ./scripts/build_macos_app.sh" >&2
  exit 1
fi
if [[ -z "$SIGN_IDENTITY" ]]; then
  echo "Missing SIGN_IDENTITY (Developer ID Application signing identity)." >&2
  exit 1
fi
if [[ -z "$NOTARY_PROFILE" ]]; then
  echo "Missing NOTARY_PROFILE (notarytool keychain profile name)." >&2
  exit 1
fi

echo "Signing:"
echo "  $APP_PATH"
echo "With identity:"
echo "  $SIGN_IDENTITY"

# --deep is pragmatic for PyInstaller bundles; runtime enables hardened runtime.
codesign --force --deep --options runtime --timestamp --sign "$SIGN_IDENTITY" "$APP_PATH"

echo
echo "Verifying signature…"
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

ZIP_PATH="$ROOT_DIR/dist/${APP_NAME}.zip"
rm -f "$ZIP_PATH"

echo
echo "Zipping for notarization:"
echo "  $ZIP_PATH"
ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

echo
echo "Submitting to Apple notarization (waits for result)…"
xcrun notarytool submit "$ZIP_PATH" --keychain-profile "$NOTARY_PROFILE" --wait

echo
echo "Stapling notarization ticket…"
xcrun stapler staple "$APP_PATH"

echo
echo "Done. Final verification:"
spctl -a -vv "$APP_PATH" || true


