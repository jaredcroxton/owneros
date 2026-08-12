#!/usr/bin/env python3
"""Assemble a second brain graph.

Inputs (same directory unless overridden):
  nodes.json   scanner output, locked schema: {memory[], gskills[], pskills[], packs[], projects[], extra[]?}
  brand.json   owner, title, colors, hub taxonomy, group order
  template.html  viewer with __GRAPH_DATA__ and __BRAND_DATA__ markers

Outputs (same directory):
  index.html        the single-file map
  scan_config.json  memory dirs for the live watcher (serve_brain.py)
  manifest.txt      id | label | description lines for /ask
"""
import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "nodes.json").read_text())
brand = json.loads((ROOT / "brand.json").read_text())

nodes = []
edges = []
seen_edges = set()
ids = set()

def add_edge(a, b):
    if not a or not b or a == b:
        return
    key = tuple(sorted((a, b)))
    if key in seen_edges:
        return
    seen_edges.add(key)
    edges.append({"source": a, "target": b})

def push(n):
    if n["id"] in ids:
        return False
    ids.add(n["id"])
    nodes.append(n)
    return True

# center + hubs from brand.json
owner = brand.get("owner", "You")
nodes.append({"id": "brain", "label": owner, "kind": "brain", "group": "brain",
              "description": brand.get("tagline", "the second brain"),
              "path": "", "url": "", "links": []})
ids.add("brain")

hub_defs = list(brand.get("hubs", []))
if not any(h.get("group") == "other" for h in hub_defs):
    hub_defs.append({"id": "hub-other", "label": "Misc", "group": "other",
                     "description": "everything else"})
hub_of = {}
for h in hub_defs:
    hid = h.get("id") or ("hub-" + h["group"])
    push({"id": hid, "label": h["label"], "kind": "hub", "group": h["group"],
          "description": h.get("description", ""), "path": "", "url": "", "links": []})
    add_edge("brain", hid)
    hub_of[h["group"]] = hid

def hub_for(group):
    return hub_of.get(group, hub_of["other"])

def clean(n, kind):
    n = dict(n)
    n.setdefault("path", "")
    n.setdefault("url", "")
    n.setdefault("links", [])
    n.setdefault("group", "other")
    if n["group"] not in hub_of and kind != "skill":
        n["group"] = "other"
    n["kind"] = kind
    n["description"] = (n.get("description") or "")[:220]
    return n

# packs
for p in data.get("packs", []):
    n = clean(p, "pack")
    if push(n):
        add_edge(n["id"], hub_for(n["group"]))

# map a skill category to a pack node id by suffix ("sales" -> "pack-02-sales")
pack_ids = [n["id"] for n in nodes if n["kind"] == "pack"]
def pack_for(cat):
    for pid in pack_ids:
        tail = re.sub(r"^pack-\d+-", "", pid)
        if tail == cat or tail.startswith(cat) or cat.startswith(tail.split("-")[0]):
            return pid
    return None

# skills (global, project-local, extra/plugin)
for key in ("gskills", "pskills", "extra"):
    for s in data.get(key, []):
        n = clean(s, s.get("kind", "skill") if key == "extra" else "skill")
        cat = n["group"]
        target = None
        if cat not in hub_of:
            target = pack_for(cat)
            n["cat"] = cat
            n["group"] = "crew" if (target and "crew" in hub_of) else "other"
        if not push(n):
            continue
        add_edge(n["id"], target or hub_for(n["group"]))

# projects
for p in data.get("projects", []):
    n = clean(p, "project")
    if push(n):
        add_edge(n["id"], hub_for(n["group"]))

# memories
memories = [clean(m, "memory") for m in data.get("memory", [])]
for m in memories:
    if push(m):
        add_edge(m["id"], hub_for(m["group"]))

# alias table for resolving memory links to real nodes
alias = {}
def learn(key, nid):
    k = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    if k and k not in alias:
        alias[k] = nid

for n in nodes:
    learn(n["id"], n["id"])
    learn(n.get("label", ""), n["id"])
    if n["id"].startswith("proj-"):
        learn(n["id"][5:], n["id"])
    if n["id"].startswith("project_"):
        learn(n["id"][8:], n["id"])
    if n["id"].startswith("pack-"):
        learn(re.sub(r"^pack-\d+-", "", n["id"]), n["id"])

resolved, unresolved = 0, 0
for m in memories:
    for raw in m.get("links", []):
        k = re.sub(r"[^a-z0-9]+", "-", str(raw).lower()).strip("-")
        target = alias.get(k)
        if not target:
            for pre in ("project-", "reference-", "feedback-", "crew-"):
                if alias.get(pre + k):
                    target = alias[pre + k]
                    break
        if target:
            add_edge(m["id"], target)
            resolved += 1
        else:
            unresolved += 1

# born dates: file birthtime, mtime fallback (genesis replay)
for n in nodes:
    n.pop("links", None)
    n.pop("cat", None)
    n["born"] = None
    p = n.get("path")
    if p and os.path.exists(p):
        try:
            st = os.stat(p)
            n["born"] = int(getattr(st, "st_birthtime", 0) or st.st_mtime)
        except OSError:
            pass

graph = {"scanned": date.today().isoformat(), "nodes": nodes, "edges": edges}
brand_payload = {
    "title": brand.get("title", "Second Brain"),
    "owner": owner,
    "bg": brand.get("bg", "#060809"),
    "colors": brand.get("colors", {}),
    "groupOrder": [h["group"] for h in hub_defs],
    "profiles": brand.get("profiles", []),
    "examples": brand.get("examples", []),
    "voiceLang": brand.get("voiceLang", ""),
}

html = (ROOT / "template.html").read_text()
html = html.replace("__GRAPH_DATA__", json.dumps(graph, separators=(",", ":")))
html = html.replace("__BRAND_DATA__", json.dumps(brand_payload, separators=(",", ":")))
(ROOT / "index.html").write_text(html)

# watcher config: unique parent dirs of memory nodes
mem_dirs = sorted({str(Path(m["path"]).parent) for m in memories if m.get("path")})
(ROOT / "scan_config.json").write_text(json.dumps({"memory_dirs": mem_dirs, "owner": owner}, indent=1))

# manifest for /ask
lines = [f"{n['id']} | {n['label']} | {n['description']}" for n in nodes if n["kind"] != "hub"]
(ROOT / "manifest.txt").write_text("\n".join(lines))

print(f"nodes={len(nodes)} edges={len(edges)} memlinks resolved={resolved} unresolved={unresolved} memory_dirs={len(mem_dirs)}")
