#!/usr/bin/env python3
"""Generate nodes.json + brand.json for the Workforce map from the live
OwnerOS /api/workforce, then build index.html via build_map.py.
Rerun any time the cabinet or workforce.json changes:
  python3 gen_nodes.py
"""
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads(urllib.request.urlopen(
    "http://localhost:4890/api/workforce", timeout=10).read())
owner = json.loads(urllib.request.urlopen(
    "http://localhost:4890/api/owner", timeout=10).read())

PALETTE = ["#5EEAD4", "#F472B6", "#22D3EE", "#A78BFA", "#FDE047", "#4ADE80",
           "#60A5FA", "#FB923C", "#38BDF8", "#E879F9", "#FCA5A5", "#86EFAC",
           "#93C5FD", "#FCD34D", "#2DD4BF", "#C4B5FD", "#F9A8D4"]

slug = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())
short = lambda n: re.sub(
    r"^crew-(core|sales|marketing|ops|hr|finance|support|docs|training|web|design|voice|my|real)?-?",
    "", n).replace("-", " ")

colors = {"brain": "#ff6b4a", "other": "#6B7280"}
hubs = []
gskills = []
for i, p in enumerate(data["packs"]):
    g = slug(p["label"])
    colors[g] = PALETTE[i % len(PALETTE)]
    working = sum(1 for s in p["skills"] if s["status"] != "ready")
    hubs.append({"id": "hub-" + g, "label": p["label"], "group": g,
                 "description": f"{len(p['skills'])} roles" +
                                (f" · {working} working" if working else "")})
    for s in p["skills"]:
        d = s.get("dossier") or {}
        status = {"active": "WORKED THIS MONTH", "live": "HAS WORKED FOR YOU",
                  "ready": "ready to work"}[s["status"]]
        desc = status + " · replaces " + \
            (d.get("replaces_role", "outsourced hours")) + " · " + \
            (d.get("replaces_salary", "")) + ". Click for the full dossier."
        gskills.append({"id": s["name"], "label": short(s["name"]),
                        "description": desc[:220], "group": g})

brand = {
    "title": "Workforce",
    "owner": owner.get("business", "My Business"),
    "tagline": "the AI workforce",
    "bg": "#0b0e13",
    "colors": colors,
    "hubs": hubs,
    "examples": ["invoice", "proposal", "onboarding"],
    "profiles": [{
        "id": "all", "label": "Everything", "mode": "dark", "groups": "all",
        "theme": {"bg": "#0b0e13", "panel": "rgba(18,21,28,0.94)",
                  "line": "rgba(255,255,255,0.08)", "text": "#eceef2",
                  "dim": "#8b93a5", "accent": "#ff6b4a"}}],
    "voiceLang": "en-AU",
}

(ROOT / "brand.json").write_text(json.dumps(brand, indent=1))
(ROOT / "nodes.json").write_text(json.dumps(
    {"memory": [], "gskills": gskills, "pskills": [], "packs": [],
     "projects": [], "extra": []}, indent=1))
print(f"nodes: {len(gskills)} roles, {len(hubs)} hubs")
subprocess.run(["python3", str(ROOT / "build_map.py")], check=True, cwd=ROOT)
print("index.html built")
