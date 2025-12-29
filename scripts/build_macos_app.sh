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

# Build a double-clickable macOS app bundle.
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "QR Code Generator" \
  app.py

echo
echo "Built app:"
echo "  $ROOT_DIR/dist/QR Code Generator.app"


