#!/bin/zsh
# OwnerOS asset pack installer. Run from the OwnerOS app folder:
#   ./assets/install.sh   (after cloning this repo into ./assets)
# Assets are local files; the OS never fetches them at runtime.
echo "OwnerOS anatomy-of-light asset pack"
ls -la "$(dirname "$0")"/*.webp "$(dirname "$0")"/*.mp4 2>/dev/null
echo "Done. Screens pick these up automatically at /assets/*."
