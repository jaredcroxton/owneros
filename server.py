#!/usr/bin/env python3
"""OwnerOS server. Local cockpit for the business.

Contract: read-only over ~/.claude/crew-state. The ONLY write path this
server has is the capture inbox at ~/.owneros/inbox. No cloud calls at
runtime; the single exception is Fish Audio transcription, which activates
only when ~/.owneros/fish.key exists (explicitly approved opt-in).
"""
import io
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOME = Path.home()
APP_DIR = Path(__file__).resolve().parent
CREW = HOME / ".claude" / "crew-state"
PROJECTS = CREW / "projects"
SKILLS_DIR = HOME / ".claude" / "skills"
OWN = HOME / ".owneros"
INBOX = OWN / "inbox"
FISH_KEY_FILE = OWN / "fish.key"
URL_FILE = OWN / "os-url.txt"
BRAIN_URL = "http://localhost:4880"

SANCTIONED = ["NOT STARTED", "IN PROGRESS", "BLOCKED", "READY FOR REVIEW",
              "DONE", "DONE_WITH_GAPS", "NO OUTPUT"]

# Files screen safe zones. Writes (rename/move) are allowed ONLY inside these
# roots, and never inside the write-protected build dirs below. crew-state is
# not a root at all: the cabinet stays read-only, full stop.
FILE_ROOTS = {"desktop": HOME / "Desktop", "captures": INBOX}
WRITE_PROTECTED = [HOME / "Desktop" / "cluade" / "second-brain-map",
                   HOME / "Desktop" / "cluade" / "crew-skill-packs"]
NEEDS_ME = {"BLOCKED", "READY FOR REVIEW"}
STALE_DAYS = 14

# Chrome refuses to load some ports (unsafe-port list) and stale servers squat
# others on this machine; walk candidates until a clean bind.
PORT_CANDIDATES = [4890, 4891, 4892, 4893, 4894, 4895, 4896, 4897, 4898, 4899,
                   4910, 4920, 4930, 4940, 4950]


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def days_since(ts):
    return max(0, int((time.time() - ts) // 86400))


def parse_handoff(path):
    """Tolerant parser. Title line, Date: line, STATUS: line, blank lines
    allowed between them (11 of 16 real records have one after the title).
    Anything that does not fit is returned parsed=False, shown as an
    unparsed record, and never modified."""
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = time.time()
    rec = {
        "skill": path.name[:-len("-handoff.md")] if path.name.endswith("-handoff.md") else path.stem,
        "file": path.name,
        "title": None, "date": None, "status": None,
        "parsed": False, "mtime": mtime,
    }
    text = read_text(path)
    if text is None:
        return rec, None
    lines = text.splitlines()
    head = [ln for ln in lines[:12] if ln.strip()]
    if head:
        rec["title"] = head[0].lstrip("# ").strip()
    for ln in head[1:8]:
        if rec["date"] is None and ln.startswith("Date:"):
            rec["date"] = ln[len("Date:"):].strip()
        elif rec["status"] is None and ln.startswith("STATUS:"):
            value = ln[len("STATUS:"):].strip()
            if value in SANCTIONED:
                rec["status"] = value
    rec["parsed"] = bool(rec["title"] and rec["date"] and rec["status"])
    return rec, text


def record_sort_key(rec):
    try:
        return datetime.strptime(rec["date"], "%Y-%m-%d").timestamp()
    except (TypeError, ValueError):
        return rec["mtime"]


def scan_projects():
    """One entry per project dir, plus unparsed entries for loose files."""
    out = []
    if not PROJECTS.is_dir():
        return out
    for entry in sorted(PROJECTS.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            records = []
            for f in sorted(entry.glob("*-handoff.md")):
                rec, _ = parse_handoff(f)
                rec["days"] = days_since(rec["mtime"])
                rec["stale"] = rec["days"] > STALE_DAYS
                records.append(rec)
            records.sort(key=record_sort_key, reverse=True)
            latest = records[0] if records else None
            mtimes = [r["mtime"] for r in records] or [entry.stat().st_mtime]
            out.append({
                "name": entry.name,
                "kind": "project",
                "records": records,
                "latest": latest,
                "days": days_since(max(mtimes)),
                "stale": days_since(max(mtimes)) > STALE_DAYS,
                "needs_me": [r for r in records if r["status"] in NEEDS_ME],
                "resume": f'claude "restore context for project {entry.name} and continue"',
            })
        elif entry.suffix == ".md":
            out.append({
                "name": entry.stem,
                "kind": "loose",
                "records": [],
                "latest": None,
                "days": days_since(entry.stat().st_mtime),
                "stale": days_since(entry.stat().st_mtime) > STALE_DAYS,
                "needs_me": [],
                "resume": f'claude "restore context for project {entry.stem} and continue"',
                "note": "unparsed record: loose file in projects/, no handoff structure",
            })
    return out


OWNER_FILE = OWN / "owner.json"


def owner():
    """Identity layer: who this OS belongs to. Absent file = Jared's defaults,
    so the original install behaves exactly as before."""
    try:
        data = json.loads(read_text(OWNER_FILE) or "{}")
    except ValueError:
        data = {}
    name = (data.get("name") or "Jared").strip() or "Jared"
    return {"name": name,
            "initial": (data.get("initial") or name[:1]).strip().upper()[:2],
            "business": (data.get("business") or "PerformOS").strip(),
            "about": (data.get("about") or
                      "AI adoption for small business: workshops, training, "
                      "an agent catalogue").strip()}


OVERLAY_FILE = OWN / "overlay.json"


def read_overlay():
    """View preferences only. Lives in ~/.owneros, never in the cabinet."""
    try:
        data = json.loads(read_text(OVERLAY_FILE) or "{}")
    except ValueError:
        data = {}
    return {"pins": [str(x) for x in data.get("pins", [])][:50],
            "stars": [str(x) for x in data.get("stars", [])][:50],
            "hidden": [str(x) for x in data.get("hidden", [])][:100]}


def api_overlay_set(payload):
    clean = {"pins": [str(x) for x in payload.get("pins", [])][:50],
             "stars": [str(x) for x in payload.get("stars", [])][:50],
             "hidden": [str(x) for x in payload.get("hidden", [])][:100]}
    OWN.mkdir(parents=True, exist_ok=True)
    OVERLAY_FILE.write_text(json.dumps(clean, indent=1), encoding="utf-8")
    return 200, {"ok": True, **clean}


MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
DATES_FILE = OWN / "dates.json"


def project_deadline(name):
    """Deadline for a project: explicit ~/.owneros/dates.json override first,
    else a monthDD token in the project name (e.g. -aug29)."""
    try:
        overrides = json.loads(read_text(DATES_FILE) or "{}")
    except ValueError:
        overrides = {}
    if name in overrides:
        try:
            return datetime.strptime(overrides[name], "%Y-%m-%d").date()
        except ValueError:
            return None
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)-?(\d{1,2})",
                  name.lower())
    if not m:
        return None
    month, day = MONTHS[m.group(1)], int(m.group(2))
    today = datetime.now().date()
    try:
        candidate = today.replace(month=month, day=day)
    except ValueError:
        return None
    if (today - candidate).days > 7:
        candidate = candidate.replace(year=candidate.year + 1)
    return candidate


def api_backup():
    import zipfile
    dest_dir = OWN / "backups"
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / ("owneros-snapshot-" +
                       datetime.now().strftime("%Y%m%d-%H%M") + ".zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for label, root in (("crew-state", CREW), ("captures-inbox", INBOX)):
            if not root.is_dir():
                continue
            for base, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    fp = Path(base) / f
                    try:
                        z.write(fp, label + "/" + str(fp.relative_to(root)))
                    except OSError:
                        continue
    subprocess.run(["open", "-R", str(path)], timeout=10)
    return 200, {"ok": True, "file": str(path), "bytes": path.stat().st_size}


def brand_name():
    text = read_text(CREW / "brand-context.md") or ""
    for ln in text.splitlines():
        if ln.startswith("#"):
            return ln.lstrip("# ").split("·")[0].strip()
    return "Unknown brand"


def api_today():
    projects = scan_projects()
    overlay = read_overlay()
    hidden = set(overlay["hidden"])
    needs = []
    for p in projects:
        # Hidden never suppresses "needs me": safety beats tidiness.
        for r in p["needs_me"]:
            needs.append({"project": p["name"], **{k: r[k] for k in
                          ("skill", "status", "date", "days")}})
    visible = [p for p in projects if p["name"] not in hidden]
    recent = sorted(visible, key=lambda p: p["days"])[:5]
    active = (read_text(CREW / "active-project") or "").strip()
    if active in hidden:
        active = "a private project"
    return {
        "date": datetime.now().strftime("%A %-d %B %Y"),
        "brand": brand_name(),
        "active_project": active,
        "needs_me": needs,
        "captures": len(list(INBOX.glob("*.md"))) if INBOX.is_dir() else 0,
        "deadlines": sorted(
            [{"project": p["name"], "date": d.strftime("%Y-%m-%d"),
              "days_left": (d - datetime.now().date()).days}
             for p in visible
             for d in [project_deadline(p["name"])]
             if d is not None and -1 <= (d - datetime.now().date()).days <= 180],
            key=lambda x: x["days_left"]),
        "hidden_count": len([p for p in projects if p["name"] in hidden]),
        "recent": [{"name": p["name"], "kind": p["kind"], "days": p["days"],
                    "stale": p["stale"],
                    "status": p["latest"]["status"] if p["latest"] else None,
                    "skill": p["latest"]["skill"] if p["latest"] else None}
                   for p in recent],
        "project_count": len(visible),
    }


LEARN_HEADS = re.compile(
    r"learn|lesson|decision|risk|watch|gotcha|avoid|next time|remaining", re.I)
BULLET = re.compile(r"^([-*]|\d+\.)\s+")


def strip_md(s):
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return s.strip()


def api_learned():
    """The self-learning loop, surfaced: lesson bullets from the newest
    handoff in the cabinet. Read-only, fresh per request."""
    best = None
    if PROJECTS.is_dir():
        for d in PROJECTS.iterdir():
            if d.is_dir():
                for f in d.glob("*-handoff.md"):
                    try:
                        m = f.stat().st_mtime
                    except OSError:
                        continue
                    if best is None or m > best[0]:
                        best = (m, d.name, f)
    if not best:
        return {"learned": None}
    mtime, proj, f = best
    rec, text = parse_handoff(f)
    points = extract_points(text)
    return {"learned": {"project": proj, "skill": rec.get("skill"),
                        "date": rec.get("date"),
                        "days": days_since(mtime), "points": points}}


def extract_points(text, cap=4):
    points, capture = [], False
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("#") or (s.startswith("**") and s.rstrip(":").endswith("**")):
            capture = bool(LEARN_HEADS.search(s))
            continue
        if capture and BULLET.match(s):
            pt = strip_md(BULLET.sub("", s))
            if pt:
                points.append(pt[:220])
        if len(points) >= cap:
            break
    if not points:
        for line in (text or "").splitlines():
            s = line.strip()
            if BULLET.match(s):
                pt = strip_md(BULLET.sub("", s))
                if pt:
                    points.append(pt[:220])
            if len(points) >= 3:
                break
    return points


def api_project_learned(name):
    """Every run's lessons for one project, newest first — the loop over time."""
    detail = api_project(name)
    if not detail:
        return None
    runs = []
    for rec in detail["records"]:
        points = extract_points(rec.get("body") or "")
        if points:
            runs.append({"date": rec.get("date"), "skill": rec.get("skill"),
                         "days": rec.get("days"), "status": rec.get("status"),
                         "points": points})
    return {"project": name, "runs": runs}


def api_project(name):
    if not re.fullmatch(r"[A-Za-z0-9._ -]+", name or "") or name in {".", ".."}:
        return None
    d = PROJECTS / name
    if d.resolve().parent != PROJECTS.resolve():
        return None
    if d.is_dir():
        records = []
        for f in sorted(d.glob("*-handoff.md")):
            rec, text = parse_handoff(f)
            rec["days"] = days_since(rec["mtime"])
            rec["stale"] = rec["days"] > STALE_DAYS
            rec["body"] = text
            records.append(rec)
        records.sort(key=record_sort_key, reverse=True)
        extras = sorted(f.name for f in d.iterdir()
                        if f.is_file() and not f.name.endswith("-handoff.md"))
        return {"name": name, "kind": "project", "records": records,
                "other_files": extras,
                "resume": f'claude "restore context for project {name} and continue"'}
    loose = PROJECTS / f"{name}.md"
    if loose.is_file():
        return {"name": name, "kind": "loose",
                "records": [{"skill": None, "file": loose.name, "title": name,
                             "date": None, "status": None, "parsed": False,
                             "days": days_since(loose.stat().st_mtime),
                             "stale": False, "body": read_text(loose)}],
                "other_files": [],
                "resume": f'claude "restore context for project {name} and continue"'}
    return None


def parse_frontmatter(path):
    text = read_text(path) or ""
    m = re.match(r"\A---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fields = {}
    for ln in m.group(1).splitlines():
        if ":" in ln and not ln.startswith(" "):
            k, _, v = ln.partition(":")
            fields[k.strip()] = v.strip()
    return fields


def api_skills():
    pack_data = json.loads(read_text(APP_DIR / "pack-map.json") or "{}")
    pack_of = pack_data.get("skills", {})
    packs = {p["id"]: {**p, "skills": []} for p in pack_data.get("packs", [])}
    unpacked = []
    for d in sorted(SKILLS_DIR.glob("crew-*")):
        if not d.is_dir():
            continue
        fm = parse_frontmatter(d / "SKILL.md")
        if not fm.get("name"):
            # Validity rule: a crew-* folder with no parseable SKILL.md is not a
            # skill. Skipped from the roster entirely, never deleted from disk.
            continue
        desc = fm.get("description", "")
        first = desc.split(". ")[0].strip()
        skill = {"name": fm["name"],
                 "description": (first + ".") if first and not first.endswith(".") else first,
                 "invoke": f"/{fm['name']}"}
        pid = pack_of.get(d.name)
        if pid in packs:
            packs[pid]["skills"].append(skill)
        else:
            unpacked.append(skill)
    return {"packs": [packs[k] for k in sorted(packs)], "unpacked": unpacked,
            "total": sum(len(p["skills"]) for p in packs.values()) + len(unpacked)}


# ---- the SOP layer: read a skill's own procedure out of its SKILL.md --------
# Every extractor is a findall, so a malformed or missing file yields empty
# lists plus a `gaps` entry. Nothing here raises. Measured: 0.35 ms per file.
SKILL_NAME = re.compile(r"\Acrew-[a-z0-9-]+\Z")
SEC_SPLIT = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.M)
# A step runs until a blank line, the next number, or the closing boilerplate.
# Anchored on the PREFIX because the corpus has two variants of the last line:
# "Final Step: Handoff Save" (74) and "Final Step: Record Save" (13).
STEP_RE = re.compile(
    r"^(\d+)\.[ \t]+(.*(?:\n(?!\s*\n|\d+\.[ \t]|\*\*Final Step)[^\n]*)*)", re.M)
LEAD_RE = re.compile(r"\A\*\*(.+?)\.?\*\*[ \t]*")
CHECK_RE = re.compile(r"^[ \t]*(?:[-*][ \t]+)?\[[ xX]?\][ \t]+(.+?)[ \t]*$", re.M)
BULLET_RE = re.compile(r"^[ \t]*[-*][ \t]+(.+?)[ \t]*$", re.M)
CREW_TICK = re.compile(r"`(crew-[a-z0-9-]+)`")
CREW_BARE = re.compile(r"crew-[a-z0-9-]+")
CREW_PATH = re.compile(r"`(~?/?\.?[^`\s]*crew-state[^`\s]*)`")
STEP0_RE = re.compile(r"\*\*Step 0:.*?\*\*(.*?)(?=\n\d+\.[ \t]|\Z)", re.S)
FINAL_RE = re.compile(r"\*\*Final Step:.*?\*\*(.*)", re.S)
STEP_CHARS = 900
LINE_CHARS = 120


def shorten(s, cap=LINE_CHARS):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    dot = s.find(". ")
    if 0 < dot < cap:
        return s[:dot + 1]
    if len(s) <= cap:
        return s
    cut = s[:cap].rsplit(" ", 1)[0]
    return cut + "…"


def skill_sections(text):
    """-> ({heading: body}, [heading order]). First of a duplicate wins."""
    parts = SEC_SPLIT.split(text or "")
    out, order = {}, []
    for i in range(1, len(parts), 2):
        head = parts[i].strip()
        if head not in out:
            out[head] = parts[i + 1]
            order.append(head)
    return out, order


def parse_skill_doc(name):
    """Deterministic deep read of one SKILL.md. Never raises."""
    empty = {"steps": [], "step0": "", "final_step": "", "verification": [],
             "guardrails": [], "handoffs": [], "reads": [], "writes": [],
             "output": "", "sections": [], "gaps": ["file"], "bytes": 0}
    if not SKILL_NAME.match(name or ""):
        return empty
    f = SKILLS_DIR / name / "SKILL.md"
    text = read_text(f)
    if not text:
        return empty
    secs, order = skill_sections(text)
    gaps = []
    wf = secs.get("Workflow", "")
    if not wf:
        gaps.append("sop")
    steps = []
    for m in STEP_RE.finditer(wf):
        raw = m.group(2)
        lead = LEAD_RE.match(raw)
        if lead:
            title, body = lead.group(1).strip(), LEAD_RE.sub("", raw)
        else:
            title, body = shorten(raw), raw
        body = re.sub(r"\s+", " ", body).strip()
        clipped = len(body) > STEP_CHARS
        if clipped:
            body = body[:STEP_CHARS].rsplit(" ", 1)[0] + "…"
        steps.append({"n": int(m.group(1)), "title": title, "text": body,
                      "clipped": clipped})
    if wf and not steps:
        gaps.append("sop-unparsed")
    s0 = STEP0_RE.search(wf)
    fin = FINAL_RE.search(wf)
    reads = sorted(set(CREW_PATH.findall(s0.group(1)))) if s0 else []
    writes = sorted(set(CREW_PATH.findall(fin.group(1)))) if fin else []
    checks = CHECK_RE.findall(secs.get("Verification", ""))
    if not checks:
        gaps.append("verification")
    rails = BULLET_RE.findall(secs.get("Guardrails", ""))
    if not rails and secs.get("Guardrails"):
        rails = [p.strip() for p in re.split(r"\n\s*\n", secs["Guardrails"])
                 if 20 <= len(p.strip()) <= 600]
    if not rails:
        gaps.append("guardrails")
    hand = sorted(set(CREW_TICK.findall(secs.get("Handoffs", ""))) - {name})
    if not hand:
        gaps.append("handoffs")
    out_fence = re.search(r"```[a-z]*\n([^\n]+)", secs.get("Output format", ""))
    artefact = ""
    if out_fence:
        artefact = re.split(r":|  ", out_fence.group(1).strip())[0].strip()[:40]
    return {"steps": steps,
            "step0": shorten(s0.group(1)) if s0 else "",
            "final_step": shorten(fin.group(1)) if fin else "",
            "verification": [shorten(c, 200) for c in checks],
            "guardrails": [shorten(g, 240) for g in rails],
            "handoffs": hand, "reads": reads, "writes": writes,
            "output": artefact, "sections": order, "gaps": gaps,
            "bytes": len(text.encode("utf-8"))}


def corpus_sig():
    """(name, mtime_ns, size) per SKILL.md. 1.03 ms. Changes on any edit."""
    try:
        return tuple(sorted(
            (p.parent.name, p.stat().st_mtime_ns, p.stat().st_size)
            for p in SKILLS_DIR.glob("crew-*/SKILL.md")))
    except OSError:
        return ()


_LINKS = {"sig": None, "index": None}


def handoff_index():
    """{skill: [skills that hand work TO it]}. The only cached thing in the
    app: 29 ms to build, memoised against the corpus signature, so a
    hand-edited SKILL.md is live on the next request."""
    sig = corpus_sig()
    if _LINKS["sig"] != sig:
        idx = {}
        for d in sorted(SKILLS_DIR.glob("crew-*")):
            if not d.is_dir():
                continue
            fm = parse_frontmatter(d / "SKILL.md")
            if not fm.get("name"):
                continue
            for target in parse_skill_doc(fm["name"])["handoffs"]:
                idx.setdefault(target, []).append(fm["name"])
        _LINKS["index"] = idx
        _LINKS["sig"] = sig
    return _LINKS["index"] or {}


def legacy_records():
    """Handoff records in the cabinet's pre-Projects pack folders. Counted,
    never migrated, never rewritten. Keyed by skill name."""
    out = {}
    if not PROJECTS.parent.is_dir():
        return out
    for d in sorted(PROJECTS.parent.iterdir()):
        if not d.is_dir() or d.name in {"projects", "projects-archive",
                                        "brands", "lessons"}:
            continue
        for f in d.glob("*-handoff.md"):
            skill = f.name[:-len("-handoff.md")]
            rec = out.setdefault(skill, {"count": 0, "folders": []})
            rec["count"] += 1
            if d.name not in rec["folders"]:
                rec["folders"].append(d.name)
    return out


def play_links():
    """{skill: {plays:[...], chains:[...]}} derived from the play library."""
    data = parse_playbook()
    known = {d.name for d in SKILLS_DIR.glob("crew-*") if d.is_dir()}
    out = {}
    for cat in data.get("categories", []):
        for play in cat.get("plays", []):
            for s in set(CREW_BARE.findall(play.get("prompt", ""))):
                if s in known:
                    out.setdefault(s, {"plays": [], "chains": []})["plays"].append(
                        {"title": play["title"], "category": cat["category"]})
    for ch in data.get("chains", []):
        steps = ch.get("steps", [])
        for i, step in enumerate(steps):
            for piece in re.split(r"\s+/\s+", step):
                s = resolve_step(piece, known)
                if s:
                    out.setdefault(s, {"plays": [], "chains": []})["chains"].append(
                        {"title": ch["title"], "position": i + 1,
                         "of": len(steps)})
    return out


def resolve_step(step, known):
    """Chain steps drop the crew- prefix and sometimes carry a parenthetical."""
    s = re.sub(r"\s*\(.*?\)", "", step or "").strip().lower()
    if not s:
        return None
    if s in known:
        return s
    if "crew-" + s in known:
        return "crew-" + s
    hits = [k for k in known if k.endswith("-" + s)]
    return hits[0] if len(hits) == 1 else None


def api_role(name):
    """Everything one role knows about itself. Fresh read, ~3 ms."""
    if not SKILL_NAME.match(name or ""):
        return None
    d = SKILLS_DIR / name
    if not (d / "SKILL.md").is_file():
        return None
    fm = parse_frontmatter(d / "SKILL.md")
    if not fm.get("name"):
        return None
    doc = parse_skill_doc(name)
    known = {x.name for x in SKILLS_DIR.glob("crew-*") if x.is_dir()}
    label = {}
    try:
        pack_data = json.loads(read_text(APP_DIR / "pack-map.json") or "{}")
        packs = {p["id"]: p["label"] for p in pack_data.get("packs", [])}
        label = {"pack": packs.get(pack_data.get("skills", {}).get(name), "")}
    except ValueError:
        label = {"pack": ""}
    runs, last = [], None
    for p in scan_projects():
        for r in p["records"]:
            if r["skill"] == name:
                runs.append({"project": p["name"], "date": r["date"],
                             "days": r["days"], "status": r["status"],
                             "points": extract_points(
                                 read_text(PROJECTS / p["name"] / r["file"]) or "")})
                last = max(last or 0, r["mtime"])
    legacy = legacy_records().get(name, {"count": 0, "folders": []})
    files = [f for f in d.rglob("*") if f.is_file()]
    links = play_links().get(name, {"plays": [], "chains": []})
    return {"name": name, "title": name, "pack": label["pack"],
            "invoke": f"/{name}", "description": fm.get("description", ""),
            "file": {"bytes": doc["bytes"], "folder_files": len(files),
                     "has_folder": len(files) > 1},
            "sop": {"steps": doc["steps"], "step0": doc["step0"],
                    "final_step": doc["final_step"]},
            "verification": doc["verification"], "guardrails": doc["guardrails"],
            "reads": doc["reads"], "writes": doc["writes"],
            "output": doc["output"],
            "works_with": {
                "downstream": [{"name": h, "known": h in known}
                               for h in doc["handoffs"]],
                "upstream": [{"name": u, "known": True}
                             for u in sorted(handoff_index().get(name, []))]},
            "used_by": links,
            "learned": {"project_runs": len(runs),
                        "legacy_records": legacy["count"],
                        "legacy_folders": legacy["folders"],
                        "runs": sorted(runs, key=lambda r: r["days"])},
            "sections": doc["sections"], "gaps": doc["gaps"]}


def skill_dir(name):
    """The only bridge from a URL parameter into ~/.claude/skills."""
    if not SKILL_NAME.match(name or ""):
        return None
    root = SKILLS_DIR.resolve()
    try:
        d = (root / name).resolve(strict=True)
    except OSError:
        return None
    return d if d.is_dir() and d.parent == root else None


def skill_bytes(name, fmt):
    """-> (blob, filename, ctype) | None. Serves bytes from OUTSIDE APP_DIR,
    the only place in the app that does, so all three guards stay."""
    if fmt not in {"md", "zip"}:
        return None
    d = skill_dir(name)
    if not d:
        return None
    if fmt == "md":
        f = d / "SKILL.md"
        if not f.is_file():
            return None
        return (f.read_bytes(), f"{name}-SKILL.md",
                "text/markdown; charset=utf-8")
    buf = io.BytesIO()
    total = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(d.rglob("*")):
            if p.is_symlink() or not p.is_file():
                continue
            try:
                if p.resolve().parent != p.parent.resolve():
                    continue
                size = p.stat().st_size
            except OSError:
                continue
            if size > 2 * 1024 * 1024 or total + size > 12 * 1024 * 1024:
                continue
            total += size
            z.write(p, arcname=str(Path(d.name) / p.relative_to(d)))
        z.writestr(f"{d.name}/ATTRIBUTION.txt",
                   "CREW skill by Jared Croxton / PerformOS.\n"
                   "Shared from OwnerOS. Keep the attribution with the file.\n")
    return (buf.getvalue(), f"{name}.zip", "application/zip")


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "note"


def api_capture(payload):
    text = (payload.get("text") or "").strip()
    if not text:
        return {"ok": False, "error": "Empty capture"}
    title = (payload.get("title") or "").strip() or text.splitlines()[0][:60]
    slug = slugify(title)
    INBOX.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = INBOX / f"{stamp}-{slug}.md"
    desc = " ".join(text.split())[:140]
    body = (f"---\nname: {slug}\ndescription: {desc}\n"
            f"captured: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"source: owneros-capture\n---\n\n# {title}\n\n{text}\n")
    path.write_text(body, encoding="utf-8")
    return {"ok": True, "file": str(path), "name": slug}


def msgpack_asr_body(audio, language="en"):
    """Minimal msgpack encoding of {audio: <bin>, language: <str>} — the shape
    Fish's ASR endpoint accepts (verified live)."""
    out = bytearray()
    out.append(0x82)
    def pack_str(s):
        b = s.encode()
        out.append(0xa0 | len(b))
        out.extend(b)
    pack_str("audio")
    out.append(0xc6)
    out.extend(len(audio).to_bytes(4, "big"))
    out.extend(audio)
    pack_str("language")
    pack_str(language)
    return bytes(out)


def api_transcribe(audio, content_type):
    key = (read_text(FISH_KEY_FILE) or "").strip()
    if not key:
        return 501, {"fish": False,
                     "error": "No Fish key at ~/.owneros/fish.key; browser speech is the fallback"}
    if not audio:
        return 400, {"fish": True, "error": "No audio received"}
    req = urllib.request.Request(
        "https://api.fish.audio/v1/asr", data=msgpack_asr_body(audio),
        method="POST",
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/msgpack"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        return 200, {"fish": True, "text": data.get("text", "")}
    except Exception as exc:
        return 502, {"fish": True, "error": f"Fish transcription failed: {exc}"}


def files_resolve(root_key, rel):
    root = FILE_ROOTS.get(root_key or "")
    if root is None or not root.is_dir():
        return None, None
    rel = (rel or "").strip().lstrip("/")
    if "\x00" in rel:
        return None, None
    target = (root / rel).resolve() if rel else root.resolve()
    if target != root.resolve() and not target.is_relative_to(root.resolve()):
        return None, None
    return root.resolve(), target


def files_write_blocked(path):
    return any(path == p.resolve() or path.is_relative_to(p.resolve())
               for p in WRITE_PROTECTED if p.exists())


def api_files_list(root_key, rel):
    root, target = files_resolve(root_key, rel)
    if target is None or not target.is_dir():
        return None
    dirs, files = [], []
    for entry in sorted(target.iterdir(), key=lambda p: p.name.lower()):
        if entry.name.startswith("."):
            continue
        try:
            st = entry.stat()
        except OSError:
            continue
        if entry.is_dir():
            dirs.append({"name": entry.name,
                         "protected": files_write_blocked(entry.resolve())})
        else:
            files.append({"name": entry.name, "size": st.st_size,
                          "days": days_since(st.st_mtime)})
    return {"root": root_key, "path": str(target.relative_to(root)) if target != root else "",
            "dirs": dirs, "files": files,
            "protected": files_write_blocked(target)}


def safe_new_name(name):
    name = (name or "").strip()
    if not name or name in {".", ".."} or "/" in name or "\x00" in name \
            or name.startswith("."):
        return None
    return name


def api_files_rename(payload):
    root, src = files_resolve(payload.get("root"), payload.get("path"))
    if src is None or not src.exists() or src == root:
        return 404, {"ok": False, "error": "File not found in a safe zone"}
    if files_write_blocked(src):
        return 403, {"ok": False, "error": "That folder is write-protected (build-critical)"}
    new_name = safe_new_name(payload.get("new_name"))
    if not new_name:
        return 400, {"ok": False, "error": "Bad name"}
    dest = src.with_name(new_name)
    if dest.exists():
        return 409, {"ok": False, "error": "A file with that name already exists"}
    src.rename(dest)
    return 200, {"ok": True, "name": new_name}


def api_files_move(payload):
    root, src = files_resolve(payload.get("root"), payload.get("path"))
    droot, dest_dir = files_resolve(payload.get("dest_root") or payload.get("root"),
                                    payload.get("dest_path"))
    if src is None or not src.exists() or src == root:
        return 404, {"ok": False, "error": "File not found in a safe zone"}
    if dest_dir is None or not dest_dir.is_dir():
        return 404, {"ok": False, "error": "Destination is not a folder in a safe zone"}
    if files_write_blocked(src) or files_write_blocked(dest_dir):
        return 403, {"ok": False, "error": "That folder is write-protected (build-critical)"}
    dest = dest_dir / src.name
    if dest.exists():
        return 409, {"ok": False, "error": "Something with that name is already there"}
    if src.is_dir() and dest_dir.is_relative_to(src):
        return 400, {"ok": False, "error": "Cannot move a folder into itself"}
    src.rename(dest)
    return 200, {"ok": True, "moved_to": str(dest)}


def api_files_reveal(payload):
    root, target = files_resolve(payload.get("root"), payload.get("path"))
    if target is None or not target.exists():
        return 404, {"ok": False, "error": "Not found in a safe zone"}
    subprocess.run(["open", "-R", str(target)], timeout=10)
    return 200, {"ok": True}


def claude_bin():
    return shutil.which("claude") or str(HOME / ".local" / "bin" / "claude")


BRIEF_DIR = OWN / "briefings"
FISH_VOICE_FILE = OWN / "fish-voice.txt"


def briefing_context():
    # Hidden projects stay out of anything Brock says out loud (video safety).
    hidden = set(read_overlay()["hidden"])
    projects = [p for p in scan_projects() if p["name"] not in hidden]
    captures = []
    if INBOX.is_dir():
        for f in sorted(INBOX.glob("*.md"),
                        key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            fm = parse_frontmatter(f)
            captures.append({"name": fm.get("name", f.stem),
                             "description": fm.get("description", "")})
    active = (read_text(CREW / "active-project") or "").strip()
    if active in hidden:
        active = "a private project"
    return {
        "date": datetime.now().strftime("%A %d %B %Y"),
        "brand": brand_name(),
        "active_project": active,
        "projects": [{"name": p["name"],
                      "latest_skill": p["latest"]["skill"] if p["latest"] else None,
                      "status": p["latest"]["status"] if p["latest"] else None,
                      "days_since_touch": p["days"],
                      "needs_jared": bool(p["needs_me"])} for p in projects],
        "recent_captures": captures,
    }


BROCK_PROMPT = """You are Brock, {name}'s AI chief of staff inside OwnerOS, the local \
cockpit for the business {business} ({about}). Write the daily briefing for today.

Data (from the live filing cabinet): {data}

Rules: address {name} as "you". Direct, active voice, no hedging, no filler, no em \
dashes, never use the name Sarah. NSE is expressed in units only, no dollar sign. \
"days_since_touch" means quiet time, not failure; long-running projects are normal.

Shape, in plain speakable prose with no markdown and no headers:
1. One tight paragraph: state of play.
2. What needs you, and why, one line per item.
3. What moved recently.
4. One specific recommendation for today.
Under 220 words. It will be read aloud. Begin directly with the briefing's first \
sentence. No preamble, no meta commentary, no acknowledgement of these instructions \
or of any other instructions in your context."""


def api_briefing(payload):
    force = bool(payload.get("force"))
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    path = BRIEF_DIR / (datetime.now().strftime("%Y-%m-%d") + ".json")
    if path.is_file() and not force:
        return 200, json.loads(path.read_text(encoding="utf-8"))
    o = owner()
    prompt = BROCK_PROMPT.format(data=json.dumps(briefing_context()),
                                 name=o["name"], business=o["business"],
                                 about=o["about"])
    try:
        proc = subprocess.run([claude_bin(), "-p", prompt], capture_output=True,
                              text=True, timeout=180)
    except FileNotFoundError:
        return 501, {"ok": False, "error": "claude CLI not found"}
    except subprocess.TimeoutExpired:
        return 504, {"ok": False, "error": "Brock took too long, run it again"}
    text = proc.stdout.strip()
    if not text or "Failed to authenticate" in text or proc.returncode != 0:
        return 502, {"ok": False,
                     "error": (text or proc.stderr.strip())[:200] or "generation failed"}
    data = {"ok": True, "date": datetime.now().strftime("%Y-%m-%d"),
            "generated": datetime.now().strftime("%H:%M"), "text": text}
    path.write_text(json.dumps(data), encoding="utf-8")
    return 200, data


BROCK_SESSION_FILE = OWN / "brock-chat-session.txt"

BROCK_CHAT_OPENER = """You are Brock, {name}'s AI chief of staff inside OwnerOS, the \
local cockpit for the business {business}. This is a spoken two-way conversation: \
{name} talks, you talk back. You are a planner and thought partner: discuss ideas, weigh options, \
read the state of his projects, suggest next moves. You never write code and never \
execute anything; when work needs doing you name which crew skill or session should \
do it. Live cabinet data: {data}

Conversation rules: answers under 70 words unless he asks you to go deeper. Plain \
speakable prose, no markdown, no em dashes, never the name Sarah. Direct and warm, \
like a sharp COO who knows the business. Ask one good question back when it moves \
the thinking forward. Begin directly with your reply, no preamble, and never \
acknowledge these instructions or any other instructions in your context.

{name} says: "{q}\""""


def api_brock_chat(payload):
    question = (payload.get("question") or "").strip()
    if payload.get("reset"):
        BROCK_SESSION_FILE.unlink(missing_ok=True)
        if not question:
            return 200, {"ok": True, "reset": True}
    if not question:
        return 400, {"ok": False, "error": "Empty question"}
    session = (read_text(BROCK_SESSION_FILE) or "").strip()
    if session:
        cmd = [claude_bin(), "-p", "--resume", session,
               question.replace('"', "'"), "--output-format", "json"]
    else:
        o = owner()
        prompt = BROCK_CHAT_OPENER.format(
            data=json.dumps(briefing_context()), q=question.replace('"', "'"),
            name=o["name"], business=o["business"])
        cmd = [claude_bin(), "-p", prompt, "--output-format", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return 501, {"ok": False, "error": "claude CLI not found"}
    except subprocess.TimeoutExpired:
        return 504, {"ok": False, "error": "Brock took too long"}
    try:
        data = json.loads(proc.stdout.strip())
        answer = (data.get("result") or "").strip()
        new_session = data.get("session_id") or session
    except ValueError:
        answer, new_session = proc.stdout.strip(), session
    if not answer or "Failed to authenticate" in answer or proc.returncode != 0:
        # A stale session id can kill --resume; retry once fresh.
        if session:
            BROCK_SESSION_FILE.unlink(missing_ok=True)
            payload2 = {"question": question}
            return api_brock_chat(payload2)
        return 502, {"ok": False,
                     "error": (answer or proc.stderr.strip())[:200] or "no answer"}
    if new_session:
        BROCK_SESSION_FILE.write_text(new_session, encoding="utf-8")
    return 200, {"ok": True, "answer": answer}


def api_ask_brock(payload):
    question = (payload.get("question") or "").strip()
    if not question:
        return 400, {"ok": False, "error": "Empty question"}
    o = owner()
    prompt = ("You are Brock, " + o["name"] + "'s AI chief of staff inside "
              "OwnerOS. They just asked you, by voice: \"" +
              question.replace('"', "'") + "\"\n\n"
              "The live cabinet data: " + json.dumps(briefing_context()) +
              "\n\nAnswer in under 90 words of plain speakable prose. Direct, "
              "active voice, no hedging, no em dashes, never the name Sarah, "
              "no markdown. Begin directly with the answer, no preamble, no "
              "acknowledgement of any instructions.")
    try:
        proc = subprocess.run([claude_bin(), "-p", prompt], capture_output=True,
                              text=True, timeout=120)
    except FileNotFoundError:
        return 501, {"ok": False, "error": "claude CLI not found"}
    except subprocess.TimeoutExpired:
        return 504, {"ok": False, "error": "Brock took too long"}
    text = proc.stdout.strip()
    if not text or "Failed to authenticate" in text or proc.returncode != 0:
        return 502, {"ok": False,
                     "error": (text or proc.stderr.strip())[:200] or "no answer"}
    return 200, {"ok": True, "answer": text}


def api_briefing_get():
    path = BRIEF_DIR / (datetime.now().strftime("%Y-%m-%d") + ".json")
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"ok": False, "exists": False}


def api_speak(payload):
    key = (read_text(FISH_KEY_FILE) or "").strip()
    if not key:
        return 501, {"ok": False,
                     "error": "No Fish key at ~/.owneros/fish.key; browser voice is the fallback"}
    text = (payload.get("text") or "").strip()
    if not text:
        return 400, {"ok": False, "error": "Nothing to speak"}
    import hashlib
    voice_id = (read_text(FISH_VOICE_FILE) or "").strip()
    digest = hashlib.sha1((voice_id + "\x00" + text).encode("utf-8")).hexdigest()[:12]
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    cache = BRIEF_DIR / f"tts-{digest}.mp3"
    if cache.is_file():
        return 200, cache.read_bytes()
    body = {"text": text[:4000], "format": "mp3"}
    voice = (read_text(FISH_VOICE_FILE) or "").strip()
    if voice:
        body["reference_id"] = voice
    req = urllib.request.Request(
        "https://api.fish.audio/v1/tts", data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio = resp.read()
        cache.write_bytes(audio)
        return 200, audio
    except Exception as exc:
        return 502, {"ok": False, "error": f"Fish voice failed: {exc}"}


def api_files_ask(payload):
    root, target = files_resolve(payload.get("root"), payload.get("path"))
    question = (payload.get("question") or "").strip()
    if target is None or not target.is_dir():
        return 404, {"ok": False, "error": "Folder not found in a safe zone"}
    if not question:
        return 400, {"ok": False, "error": "Empty question"}
    listing, count = [], 0
    for base, dirnames, filenames in os.walk(target):
        depth = Path(base).relative_to(target).parts
        if len(depth) >= 2:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.startswith("."):
                continue
            listing.append(str(Path(base).relative_to(target) / f))
            count += 1
            if count >= 200:
                break
        if count >= 200:
            break
    prompt = ("You are the files assistant inside OwnerOS, " + owner()["name"] +
              "'s local business cockpit. Folder: " + str(target) +
              "\nContents (max 200 shown):\n"
              + "\n".join(listing) +
              "\n\nQuestion: " + question +
              "\nAnswer briefly and concretely. Suggest renames or moves as plain "
              "suggestions; you cannot execute anything.")
    try:
        proc = subprocess.run([claude_bin(), "-p", prompt], capture_output=True,
                              text=True, timeout=90)
        answer = proc.stdout.strip() or proc.stderr.strip()[:300]
        return 200, {"ok": True, "answer": answer}
    except FileNotFoundError:
        return 501, {"ok": False, "error": "claude CLI not found on this machine"}
    except subprocess.TimeoutExpired:
        return 504, {"ok": False, "error": "The assistant took too long"}


def api_workforce():
    """The skill deck as a workforce: dossiers from workforce.json plus live
    status computed from the cabinet's handoff records."""
    skills_data = api_skills()
    try:
        dossiers = {d["name"]: d for d in
                    json.loads(read_text(APP_DIR / "workforce.json") or "[]")}
    except ValueError:
        dossiers = {}
    usage = {}
    for p in scan_projects():
        for r in p["records"]:
            u = usage.setdefault(r["skill"], {"runs": 0, "last_mtime": 0})
            u["runs"] += 1
            u["last_mtime"] = max(u["last_mtime"], r["mtime"])
    legacy = legacy_records()
    packs = []
    for p in skills_data["packs"]:
        if not p["skills"]:
            continue
        out = []
        for s in p["skills"]:
            u = usage.get(s["name"])
            last_days = days_since(u["last_mtime"]) if u else None
            status = ("active" if u and last_days <= 30 else
                      "live" if u else "ready")
            leg = legacy.get(s["name"], {"count": 0})
            # Deliberately NOT folded into `runs`: project runs and legacy
            # pack-folder records are different truths and are worded apart.
            out.append({**s, "dossier": dossiers.get(s["name"]),
                        "status": status, "runs": u["runs"] if u else 0,
                        "last_days": last_days,
                        "legacy_records": leg["count"],
                        "has_sop": (SKILLS_DIR / s["name"] / "SKILL.md").is_file()})
        packs.append({"label": p["label"], "skills": out})
    if skills_data["unpacked"]:
        packs.append({"label": "Unfiled", "skills": [
            {**s, "dossier": dossiers.get(s["name"]), "status": "ready",
             "runs": 0, "last_days": None,
             "legacy_records": legacy.get(s["name"], {"count": 0})["count"],
             "has_sop": False} for s in skills_data["unpacked"]]})
    return {"business": owner()["business"], "packs": packs,
            "total": sum(len(p["skills"]) for p in packs),
            "capabilities": 108}


def parse_playbook():
    """Parse playbook.md (app-owned copy of the CREW plays library) fresh per
    request. Tolerant: a play missing fields still renders with what it has."""
    text = read_text(APP_DIR / "playbook.md") or ""
    main, _, chain_part = text.partition("\n# Chain plays")

    def field(block, name):
        m = re.search(r"\*\*" + name + r":\*\*\s*(.+)", block)
        return m.group(1).strip() if m else ""

    categories = []
    for cat_block in re.split(r"\n## ", main)[1:]:
        cat_name = cat_block.split("\n", 1)[0].strip()
        plays = []
        for p_block in re.split(r"\n### ", cat_block)[1:]:
            title = p_block.split("\n", 1)[0].strip()
            intents = [s.strip() for s in field(p_block, "Intents").split(",")
                       if s.strip()]
            plays.append({"title": title,
                          "when": field(p_block, "When"),
                          "prompt": field(p_block, "Prompt").strip("`"),
                          "you_get": field(p_block, "You get"),
                          "next": field(p_block, "Next"),
                          "tip": field(p_block, "Tip"),
                          "intents": intents})
        if plays:
            categories.append({"category": cat_name, "plays": plays})

    chains = []
    for c_block in re.split(r"\n### ", chain_part)[1:]:
        title = c_block.split("\n", 1)[0].strip()
        steps = re.findall(r"^\d+\.\s*`([^`]+)`", c_block, re.M)
        chains.append({"title": title, "steps": steps,
                       "note": field(c_block, "Note")})

    return {"categories": categories, "chains": chains,
            "total_plays": sum(len(c["plays"]) for c in categories)}


def api_brands():
    """Read-only listing of brand drawers for the new-project form."""
    active = brand_name()
    drawers = []
    brands_dir = CREW / "brands"
    if brands_dir.is_dir():
        drawers = sorted(d.name for d in brands_dir.iterdir()
                         if d.is_dir() and not d.name.startswith("."))
    return {"active": active, "drawers": drawers}


def api_dates_set(payload):
    project = (payload.get("project") or "").strip()
    date_str = (payload.get("date") or "").strip()
    if not project or "/" in project or "\x00" in project:
        return 400, {"ok": False, "error": "Bad project name"}
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return 400, {"ok": False, "error": "Date must be YYYY-MM-DD"}
    try:
        dates = json.loads(read_text(DATES_FILE) or "{}")
    except ValueError:
        dates = {}
    dates[project] = date_str
    OWN.mkdir(parents=True, exist_ok=True)
    DATES_FILE.write_text(json.dumps(dates, indent=1), encoding="utf-8")
    return 200, {"ok": True, "project": project, "date": date_str}


def api_health():
    brain = False
    try:
        with urllib.request.urlopen(BRAIN_URL, timeout=1.5):
            brain = True
    except Exception:
        pass
    return {"ok": True, "brain": brain, "brain_url": BRAIN_URL,
            "fish": FISH_KEY_FILE.is_file(),
            "inbox": str(INBOX), "crew_state": str(CREW)}


ROUTES = {"/": "today.html", "/today": "today.html", "/projects": "projects.html",
          "/brain": "brain.html", "/capture": "capture.html",
          "/launch": "launch.html", "/roadmap": "roadmap.html",
          "/files": "files.html", "/plays": "plays.html"}


class Handler(BaseHTTPRequestHandler):
    server_version = "OwnerOS/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))

    def send_json(self, obj, code=200):
        blob = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(blob)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(blob)

    def send_download(self, blob, filename, ctype):
        """The only response in the app carrying bytes from outside APP_DIR.
        filename is built from a name that already matched ^crew-[a-z0-9-]+$."""
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(blob)))
        self.send_header("Content-Disposition",
                         'attachment; filename="%s"' % filename)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(blob)

    def send_file(self, rel):
        path = (APP_DIR / rel.lstrip("/")).resolve()
        if not path.is_relative_to(APP_DIR) or not path.is_file():
            self.send_json({"error": "not found"}, 404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        blob = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/api/today":
            return self.send_json(api_today())
        if url.path == "/api/projects":
            return self.send_json({"projects": scan_projects()})
        if url.path == "/api/project":
            data = api_project((q.get("name") or [""])[0])
            return self.send_json(data if data else {"error": "unknown project"},
                                  200 if data else 404)
        if url.path == "/api/skills":
            return self.send_json(api_skills())
        if url.path == "/api/health":
            return self.send_json(api_health())
        if url.path == "/api/events":
            return self.proxy_events()
        if url.path == "/api/briefing":
            return self.send_json(api_briefing_get())
        if url.path == "/api/overlay":
            return self.send_json(read_overlay())
        if url.path == "/api/brands":
            return self.send_json(api_brands())
        if url.path == "/api/plays":
            return self.send_json(parse_playbook())
        if url.path == "/api/owner":
            return self.send_json(owner())
        if url.path == "/api/role":
            data = api_role((q.get("name") or [""])[0])
            return self.send_json(data if data else {"error": "unknown role"},
                                  200 if data else 404)
        if url.path == "/api/skill-file":
            fmt = (q.get("format") or ["md"])[0]
            if fmt not in {"md", "zip"}:
                return self.send_json({"error": "bad format"}, 400)
            got = skill_bytes((q.get("name") or [""])[0], fmt)
            if not got:
                return self.send_json({"error": "unknown role"}, 404)
            blob, filename, ctype = got
            return self.send_download(blob, filename, ctype)
        if url.path == "/api/learned":
            proj = (q.get("project") or [""])[0]
            if proj:
                data = api_project_learned(proj)
                return self.send_json(data if data else {"error": "unknown"},
                                      200 if data else 404)
            return self.send_json(api_learned())
        if url.path == "/api/workforce":
            return self.send_json(api_workforce())
        if url.path == "/api/files":
            data = api_files_list((q.get("root") or ["desktop"])[0],
                                  (q.get("path") or [""])[0])
            return self.send_json(data if data else {"error": "not a safe zone"},
                                  200 if data else 404)
        if url.path in ROUTES:
            return self.send_file(ROUTES[url.path])
        return self.send_file(url.path)

    def proxy_events(self):
        """Same-origin relay of the Brain's SSE stream so pages can listen
        without cross-origin trouble. Read-only pass-through."""
        try:
            # Brain emits a keepalive ping every 15s; read timeout must outlive it.
            upstream = urllib.request.urlopen(BRAIN_URL + "/events", timeout=45)
        except Exception:
            self.send_json({"error": "brain offline"}, 502)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                line = upstream.readline()
                if not line:
                    break
                self.wfile.write(line)
                if line == b"\n":
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            upstream.close()

    def do_HEAD(self):
        url = urlparse(self.path)
        rel = ROUTES.get(url.path, url.path.lstrip("/"))
        path = (APP_DIR / rel).resolve()
        if path.is_relative_to(APP_DIR) and path.is_file():
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(path))[0]
                             or "application/octet-stream")
            self.send_header("Content-Length", str(path.stat().st_size))
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if url.path == "/api/capture":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            result = api_capture(payload)
            return self.send_json(result, 200 if result.get("ok") else 400)
        if url.path == "/api/transcribe":
            code, result = api_transcribe(raw, self.headers.get("Content-Type",
                                                                "audio/webm"))
            return self.send_json(result, code)
        if url.path == "/api/briefing":
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except ValueError:
                payload = {}
            code, result = api_briefing(payload)
            return self.send_json(result, code)
        if url.path == "/api/backup":
            code, result = api_backup()
            return self.send_json(result, code)
        if url.path == "/api/overlay":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            code, result = api_overlay_set(payload)
            return self.send_json(result, code)
        if url.path == "/api/dates":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            code, result = api_dates_set(payload)
            return self.send_json(result, code)
        if url.path == "/api/brock-chat":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            code, result = api_brock_chat(payload)
            return self.send_json(result, code)
        if url.path == "/api/ask-brock":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            code, result = api_ask_brock(payload)
            return self.send_json(result, code)
        if url.path == "/api/speak":
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            code, result = api_speak(payload)
            if code == 200:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(result)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(result)
                return
            return self.send_json(result, code)
        if url.path in ("/api/files/rename", "/api/files/move", "/api/files/ask",
                        "/api/files/reveal"):
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                return self.send_json({"ok": False, "error": "bad json"}, 400)
            handler = {"/api/files/rename": api_files_rename,
                       "/api/files/move": api_files_move,
                       "/api/files/ask": api_files_ask,
                       "/api/files/reveal": api_files_reveal}[url.path]
            code, result = handler(payload)
            return self.send_json(result, code)
        return self.send_json({"error": "not found"}, 404)


def pick_port():
    forced = os.environ.get("OWNEROS_PORT")
    candidates = [int(forced)] if forced else PORT_CANDIDATES
    for port in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    raise SystemExit("OwnerOS: no free port in candidate list")


def main():
    port = pick_port()
    OWN.mkdir(parents=True, exist_ok=True)
    INBOX.mkdir(parents=True, exist_ok=True)
    url = f"http://localhost:{port}"
    URL_FILE.write_text(url + "\n", encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"OwnerOS live at {url}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
