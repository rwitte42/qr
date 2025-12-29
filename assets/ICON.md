## App icon (optional)

If you want a custom icon for the packaged `.app`, create an `.icns` file and build with:

```bash
QR_ICON_ICNS="/absolute/path/to/icon.icns" ./scripts/build_macos_app.sh
```

One common way to create `icon.icns` on macOS:

```bash
mkdir -p icon.iconset
# Put PNGs in icon.iconset/ named like:
# icon_16x16.png, icon_32x32.png, icon_128x128.png, icon_256x256.png, icon_512x512.png
iconutil -c icns icon.iconset
```


