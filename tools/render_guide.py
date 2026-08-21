#!/usr/bin/env python3
"""Render the shipped room guides with Fish Audio, once, on the maintainer's Mac.

Reads assets/guide/guide.json, and for every room whose text changed since the
last render (sha of voice + text) calls Fish TTS with the guide voice and writes
assets/guide/<key>.mp3. Owners never run this: the mp3s ship in the repo and play
locally, so no Fish key is needed on their Mac.

Usage:  python3 tools/render_guide.py            render what changed
        python3 tools/render_guide.py --force    render everything
        python3 tools/render_guide.py --check    exit 1 if any clip is out of date

Needs ~/.owneros/fish.key. Uses guide.json's "voice", not ~/.owneros/fish-voice.txt,
so the guide voice and Brock's briefing voice can differ.
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
GUIDE = APP / "assets" / "guide"
INDEX = GUIDE / "guide.json"
KEY_FILE = Path.home() / ".owneros" / "fish.key"


def main():
    force = "--force" in sys.argv
    check = "--check" in sys.argv
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    voice = data["voice"]
    stale = []
    for key, room in data["rooms"].items():
        sha = hashlib.sha1((voice + "\x00" + room["text"]).encode("utf-8")).hexdigest()[:12]
        if force or room.get("sha") != sha or not (GUIDE / f"{key}.mp3").is_file():
            stale.append((key, room, sha))
    if check:
        for key, _, _ in stale:
            print("out of date:", key)
        sys.exit(1 if stale else 0)
    if not stale:
        print("all clips current")
        return
    api_key = KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.is_file() else ""
    if not api_key:
        sys.exit("no Fish key at ~/.owneros/fish.key")
    for key, room, sha in stale:
        body = {"text": room["text"], "format": "mp3", "reference_id": voice}
        req = urllib.request.Request(
            "https://api.fish.audio/v1/tts", data=json.dumps(body).encode("utf-8"),
            method="POST", headers={"Authorization": f"Bearer {api_key}",
                                    "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio = resp.read()
        (GUIDE / f"{key}.mp3").write_bytes(audio)
        room["sha"] = sha
        print(f"rendered {key}.mp3  {len(audio) // 1024} KB")
    INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
