"""Fleet failure scanner (doctor lane eyes) plus the round line and lane tokens.

Reads the OpenCode session history read-only; writes only to the skill-doctor
state directory (never into this public repo).

    python tools/fleet_failures.py scan [--hours N] [--from ISO --to ISO] [--db PATH]
    python tools/fleet_failures.py loads [--hours N] [--db PATH]
    python tools/fleet_failures.py compare <skill> [--db PATH] [--csv PATH] [--before]
    python tools/fleet_failures.py lanes [--db PATH]
    python tools/fleet_failures.py round-line [--db PATH] [--check]

The database path comes from --db, else OPENCODE_DB, else the local share default.
It is always opened read-only (file: URI with mode=ro).
The state directory is SKILLDOCTOR_DIR, else the skill-doctor state folder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import finish_proof as fp  # noqa: E402  (one loads counter: S1/S2 and `loads` share skill_loads)

STATE_DIR = Path(os.environ.get("SKILLDOCTOR_DIR") or "C:/Users/me/.empire/state/skilldoctor/")
EMPIRE = Path(os.environ.get("EMPIRE_JSON") or "C:/Users/me/Desktop/center/empire.json")
WINDOW_H = 48

FAMILY = {
    "pwsh-for-bash-writers": "pwsh",
    "git-one-branch": "git",
    "real-browser-automation": "browser",
    "bevy-rust-ecs": "bevy",
}

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_Q = re.compile(r"\"[^\"\n]{0,300}\"|'[^'\n]{0,300}'|`[^`\n]{0,300}`")
_P = re.compile(r"[A-Za-z]:[\\/][^\s:;,)\]]*|(?:\/[\w.@-]+){2,}")
_ID = re.compile(r"\b(?:ses|msg|prt|call|toolu)_\w+")
_H = re.compile(r"\b[0-9a-f]{7,40}\b", re.I)
_N = re.compile(r"\d+")
_WS = re.compile(r"\s+")
_URL = re.compile(r"https?://([^/\s)\"']+)[^\s)\"']*")


def norm(s: object) -> str:
    """Same blanking as the fleet meter: hosts, quotes, paths, ids, hashes, numbers."""
    t = _ANSI.sub("", str(s or ""))

    def _host(m: re.Match) -> str:
        return "<" + re.sub(r"^www\.", "", m.group(1)) + ">"

    t = _URL.sub(_host, t)
    t = _Q.sub("Q", t)
    t = _P.sub("PATH", t)
    t = _ID.sub("ID", t)
    t = _H.sub("H", t)
    t = _N.sub("N", t)
    return _WS.sub(" ", t).strip()[:80]


def head_of(cmd: object) -> str:
    c = re.sub(r"^\s*cd\s+(\"[^\"]*\"|'[^']*'|\S+)\s*(?:&&|;)\s*", "", str(cmd or "")).strip()
    first = re.split(r"\|\||&&|[|;\n]", c)[0].replace("\"", "").replace("'", "").replace("`", "").strip().split()
    two = 2 if first and re.match(r"^(git|gh|cargo|node|npm|npx|dotnet|python|py|pwsh|powershell)$", first[0], re.I) else 1
    return " ".join(first[:two])[:40]


def chained_of(cmd: object) -> list[str]:
    c = re.sub(r"\"[^\"]*\"|'[^']*'", "Q", str(cmd or ""))
    c = re.sub(r"^\s*cd\s+\S+\s*(?:&&|;)\s*", "", c)
    out: list[str] = []
    for chunk in re.split(r"\|\||&&|[|;\n]", c)[1:]:
        w = re.sub(r"^\$\w+\s*=\s*\(?", "", chunk.strip()).split()[0] if chunk.strip().split() else ""
        if w and re.match(r"^[\w.-]+$", w) and w not in out:
            out.append(w)
    return out[:3]


def base_of(p: object) -> str:
    return str(p or "").replace("\\", "/").split("/")[-1][:60]


_PW_NOTREC = re.compile(r"The term '([^']+)' is not recognized as a name of a cmdlet")
_PW_PARSER = re.compile(r"ParserError|ParseException")
_PW_DEVNULL = re.compile(r"Could not find a part of the path '?C:\\dev\\null", re.I)
_PW_AMBIG = re.compile(r"parameter name 'u' is ambiguous")
_PW_DATEU = re.compile(r"\bdate\s+-u")
_PW_FLAG_OUT = re.compile(r"(?:A parameter cannot be found that matches|Parameter cannot be processed because) (?:the )?parameter name '([a-zA-Z]{1,3})'")
_PW_FLAG_CMD = re.compile(r"\b(ls|rm|cp|mv|cat|echo|sort|mkdir|head|tail|grep|date|diff|cd)\s+-[a-zA-Z]{1,3}\b")
_GIT_WORD = re.compile(r"\bgit\b")
_GIT_OUT = [
    (re.compile(r"pathspec '[^']*' did not match any file"), None),
    (re.compile(r"nothing to commit|no changes added to commit"), None),
    (re.compile(r"would be overwritten by (merge|checkout)|commit your changes or stash them|untracked working tree files would be overwritten"), None),
    (re.compile(r"cannot pull with rebase"), None),
    (re.compile(r"index\.lock"), None),
    (re.compile(r"! \[rejected\]|non-fast-forward|Updates were rejected"), re.compile(r"\bgit\b[^\n;|]*\bpush\b")),
    (re.compile(r"CONFLICT \(|Automatic merge failed"), re.compile(r"\bgit\b[^\n;|]*\b(pull|merge)\b")),
]
_C = r"\bgit\s+(?:-C\s+\S+\s+)?"
_GIT_RISKY = [
    re.compile(_C + r"add\s+(-A|--all|\.)(\s|$|;|\|)"),
    re.compile(_C + r"commit\b[^\n;|]*\s-[a-zA-Z]*a[a-zA-Z]*(\s|$)|\bgit\s+commit\b[^\n;|]*--all\b"),
    re.compile(_C + r"commit\b[^\n;|]*--amend"),
    re.compile(_C + r"rebase\b|\bgit\s+pull\b[^\n;|]*--rebase(?!=false)"),
    re.compile(_C + r"push\b[^\n;|]*(--force|\s-f(\s|$)|--force-with-lease)"),
    re.compile(_C + r"reset\s+--hard"),
    re.compile(_C + r"stash(\s+(push|save|pop|apply|drop|clear))?(\s|$|;|\|)"),
    re.compile(_C + r"checkout\s+(--\s|HEAD\s+--\s)"),
    re.compile(_C + r"restore\s+(?!--staged)"),
    re.compile(_C + r"clean\s+-[a-z]*f"),
    re.compile(_C + r"branch\s+-D\b"),
]
_GIT_STASH_READ = re.compile(r"\bgit\s+stash\s+(list|show)\b")
_BROWSER = re.compile(r"playwright|puppeteer|chromedriver|selenium|--remote-debugging|--headless|msedge|chrome\.exe|DevToolsActivePort", re.I)
_BEVY = re.compile(r"bevy", re.I)


def classify_call(tool: str, status: str, err: str, out40: str, cmd: str, filep: str,
                   notrec: int, term: str, devnull: int) -> tuple[str, str | None, str | None, str | None]:
    """Meter-compatible outcome, flag, fingerprint and head for one tool call."""
    wrongshell = tool == "bash" and (notrec > 0 or devnull > 0)
    outcome = "error" if status == "error" else ("hidden" if wrongshell else "ok")
    denied = bool(re.search(r"prevents you from using this specific tool call", err))
    if denied:
        flag: str | None = "denied"
    elif wrongshell:
        flag = "wrongshell"
    elif tool == "read" and err.startswith("File not found"):
        flag = "missing"
    elif tool in ("grep", "glob") and status == "completed" and out40.startswith("No files found"):
        flag = "empty"
    elif tool == "bash" and re.match(r"\s*cd\s", cmd or ""):
        flag = "cd"
    else:
        flag = None
    head = head_of(cmd) if tool == "bash" else (base_of(filep) if filep else None)
    fps: str | None = None
    if outcome != "ok":
        if denied:
            more = chained_of(cmd) if tool == "bash" else []
            fps = f"{tool} denied: {head or '?'}{(' + ' + ', '.join(more)) if more else ''}"
        elif wrongshell:
            if notrec > 0:
                m = re.search(r"The term '([^']+)'", term or "")
                fps = f"bash pwsh: '{m.group(1) if m else '?'}' is not a pwsh command"
            else:
                fps = "bash pwsh: 2>/dev/null"
        elif tool == "webfetch" and re.search(r"status code", err, re.I):
            code = (re.search(r"\b(\d{3}) (?:GET|POST|HEAD)\b", err) or [None, "?"])[1]
            hm = re.search(r"https?://(?:www\.)?([^/\s)]+)", err)
            fps = f"webfetch {code} {hm.group(1) if hm else '?'}"
        elif err.startswith("File not found"):
            body = norm(re.sub(r"^File not found:\s*", "", err)).replace("PATH", base_of(filep) or "PATH")
            fps = f"read missing: {body}"
        else:
            fps = f"{tool}: {norm(err or out40)}"
    return outcome, flag, fps, head


def family_of(tool: str, cmd: str, text: str) -> set[str]:
    """Failure families a call belongs to (one entry per family per call)."""
    hit: set[str] = set()
    if _BEVY.search((cmd or "") + " " + (text or "")):
        hit.add("bevy")
    if tool != "bash":
        return hit
    out, cmd = text or "", cmd or ""
    if _PW_NOTREC.search(out) or _PW_PARSER.search(out) or _PW_DEVNULL.search(out):
        hit.add("pwsh")
    if (_PW_AMBIG.search(out) and _PW_DATEU.search(cmd)) or (_PW_FLAG_OUT.search(out) and _PW_FLAG_CMD.search(cmd)):
        hit.add("pwsh")
    if _GIT_WORD.search(cmd):
        for rx_out, rx_cmd in _GIT_OUT:
            if rx_out.search(out) and (rx_cmd is None or rx_cmd.search(cmd)):
                hit.add("git")
        for n, rx in enumerate(_GIT_RISKY):
            if rx.search(cmd) and not (n == 6 and _GIT_STASH_READ.search(cmd)):
                hit.add("git")
                break
    if _BROWSER.search(cmd):
        hit.add("browser")
    return hit


def resolve_db(given: str | None) -> Path:
    raw = given or os.environ.get("OPENCODE_DB") or str(Path.home() / ".local" / "share" / "opencode" / "opencode.db")
    return Path(raw).expanduser()


def connect_ro(db: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True, timeout=30)


def repo_dirs(empire: Path = EMPIRE) -> list[tuple[str, str]]:
    try:
        doc = json.loads(empire.read_text(encoding="utf-8-sig"))
    except OSError:
        return []
    pairs = [(n, str(r["dir"]).replace("\\", "/").lower().rstrip("/")) for n, r in (doc.get("repos") or {}).items()]
    return sorted(pairs, key=lambda p: -len(p[1]))


def repo_of(directory: str | None, dirs: list[tuple[str, str]]) -> str:
    d = (directory or "").replace("\\", "/").lower().rstrip("/")
    for name, base in dirs:
        if d == base or d.startswith(base + "/"):
            return name
    return "other"


def parse_ms(s: str) -> float:
    """ISO-8601 instant (trailing Z accepted) to epoch milliseconds."""
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000


def scan_db(db: Path, hours: float, dirs: list[tuple[str, str]], now_ms: float | None = None,
            from_ms: float | None = None, to_ms: float | None = None) -> dict:
    """Fingerprint classes plus family counts for the window (read-only).

    Default is the trailing `hours`. Pass `from_ms`/`to_ms` to scan the exact
    window a center metrics.json entry covers, so the tolerance check compares
    the same fingerprint over the same window instead of two drifting windows.
    Parts are bucketed by time_created, the same clock the meter stores as
    `calls.at`; sessions still filter by time_updated on both sides.
    """
    now = time.time() * 1000 if now_ms is None else now_ms
    lo = from_ms if from_ms is not None else now - hours * 3_600_000
    hi = to_ms
    con = connect_ro(db)
    try:
        if hi is None:
            sess = dict(con.execute("select id, directory from session where time_updated > ?", (lo,)))
            agents = dict(con.execute("select id, agent from session where time_updated > ?", (lo,)))
        else:
            sess = dict(con.execute("select id, directory from session where time_updated > ? and time_updated <= ?", (lo, hi)))
            agents = dict(con.execute("select id, agent from session where time_updated > ? and time_updated <= ?", (lo, hi)))
        classes: dict[str, dict] = {}
        families: dict[str, dict[str, int]] = {"pwsh": {}, "git": {}, "browser": {}, "bevy": {}}
        scanned = fails = 0
        q = ("select session_id, json_extract(data,'$.tool'), json_extract(data,'$.state.status'), "
             "substr(json_extract(data,'$.state.error'),1,400), "
             "substr(json_extract(data,'$.state.input.command'),1,300), "
             "json_extract(data,'$.state.input.filePath'), "
             "substr(json_extract(data,'$.state.output'),1,40), "
             "substr(json_extract(data,'$.state.output'),1,400), "
             "instr(json_extract(data,'$.state.output'),'is not recognized as a name of a cmdlet'), "
             "substr(json_extract(data,'$.state.output'),max(1,instr(json_extract(data,'$.state.output'),'is not recognized')-60),80), "
             "instr(json_extract(data,'$.state.output'),'C:\\dev\\null') "
             "from part where time_created > ?"
             + (" and time_created <= ?" if hi is not None else "")
             + " and json_extract(data,'$.type')='tool'")
        args = (lo,) if hi is None else (lo, hi)
        for sid, tool, status, err, cmd, filep, out40, out400, notrec, term, devnull in con.execute(q, args):
            scanned += 1
            if status not in ("completed", "error"):
                continue
            tool, status = tool or "", status or ""
            err, cmd, filep, out40, out400 = err or "", cmd or "", filep or "", out40 or "", out400 or ""
            repo = repo_of(sess.get(sid), dirs)
            agent = (agents.get(sid) or "?").removesuffix("-paid")
            _o, _f, fps, _h = classify_call(tool, status, err, out40, cmd, filep, notrec or 0, term or "", devnull or 0)
            if fps:
                fails += 1
                c = classes.setdefault(fps, {"n": 0, "repos": {}, "agents": {}})
                c["n"] += 1
                c["repos"][repo] = c["repos"].get(repo, 0) + 1
                c["agents"][agent] = c["agents"].get(agent, 0) + 1
            for fam in family_of(tool, cmd, (err + "\n" + out400)):
                families[fam][repo] = families[fam].get(repo, 0) + 1
        out: dict = {"hours": hours, "scanned": scanned, "failed": fails, "classes": classes, "families": families}
        if from_ms is not None:
            out["from"] = datetime.fromtimestamp(from_ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        if hi is not None:
            out["to"] = datetime.fromtimestamp(hi / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        return out
    finally:
        con.close()


def loads_detail(db: Path, hours: float = 24, now_ms: float | None = None) -> dict[tuple[str, str], int]:
    """Skill loads by (skill, repo), same filters as finish_proof.skill_loads."""
    skills = fp._skill_names(fp.SKILLS)
    own = fp.ROOT
    cutoff = (time.time() * 1000 if now_ms is None else now_ms) - hours * 3_600_000
    con = connect_ro(db)
    try:
        sessions = dict(con.execute("select id, directory from session where time_updated > ?", (cutoff,)))
        out: dict[tuple[str, str], int] = {}
        for sid, data in con.execute(
                "select session_id, data from part where time_created > ? and data like ?", (cutoff, '%"tool":"skill"%')):
            try:
                part = json.loads(data)
            except ValueError:
                continue
            name = ((part.get("state") or {}).get("input") or {}).get("name")
            repo = fp._repo_of(sessions.get(sid) or "", own) if part.get("tool") == "skill" and name in skills else None
            if repo and name:
                out[(name, repo)] = out.get((name, repo), 0) + 1
        return out
    finally:
        con.close()


def read_rows(path: Path) -> list[list[str]]:
    try:
        return [r for r in csv.reader(path.read_text(encoding="utf-8-sig").splitlines()) if r]
    except OSError:
        return []


def skill_now(skill: str, db: Path, dirs: list[tuple[str, str]], hours: float = WINDOW_H) -> int:
    """48 h count of the class a skill targets (the number the installer records)."""
    res = scan_db(db, hours, dirs)
    if skill in FAMILY:
        return sum(res["families"][FAMILY[skill]].values())
    needle = skill.lower().replace("-", " ").split()[0]
    return sum(v["n"] for k, v in res["classes"].items() if needle in k.lower())


def skill_before(skill: str, path: Path) -> int:
    total = 0
    for i, r in enumerate(read_rows(path)):
        if i == 0 or len(r) < 6:
            continue
        if r[2].strip() == skill and r[3].strip().lower() == "adopted":
            try:
                total += int(float(r[4].strip() or 0))
            except ValueError:
                pass
    return total


def verdict_for(skill: str, before: float, after: float) -> str:
    if skill in ("real-browser-automation", "bevy-rust-ecs"):
        return "UP" if after > before else ("FLAT" if after == before else "DOWN")
    if before > 0 and after * 2 <= before:
        return "HALVED"
    return "DOWN" if after < before else ("FLAT" if after == before else "UP")


def cmd_scan(a: argparse.Namespace) -> int:
    db = resolve_db(a.db)
    if not db.is_file():
        print(f"no opencode.db at {db}")
        return 1
    from_ms = parse_ms(a.from_) if a.from_ else None
    to_ms = parse_ms(a.to) if a.to else None
    res = scan_db(db, a.hours, repo_dirs(), from_ms=from_ms, to_ms=to_ms)
    top = sorted(res["classes"].items(), key=lambda kv: -kv[1]["n"])[:5]
    for fps, v in top:
        print(f"{v['n']:6d} {fps}")
    state = STATE_DIR
    state.mkdir(parents=True, exist_ok=True)
    doc = {"generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "hours": res["hours"], "scanned": res["scanned"], "failed": res["failed"],
           "classes": {k: {"n": v["n"], "repos": v["repos"], "agents": v["agents"]} for k, v in
                       sorted(res["classes"].items(), key=lambda kv: -kv[1]["n"])},
           "families": res["families"]}
    if "from" in res:
        doc["from"] = res["from"]
    if "to" in res:
        doc["to"] = res["to"]
    (state / "failures.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return 0


def cmd_loads(a: argparse.Namespace) -> int:
    db = resolve_db(a.db)
    if not db.is_file():
        print(f"no opencode.db at {db}")
        return 1
    totals = fp.skill_loads(db, hours=a.hours)
    detail = loads_detail(db, hours=a.hours)
    for (skill, repo), n in sorted(detail.items()):
        print(f"{n:5d} {skill} {repo}")
    seen = ", ".join(f"{r} {n}" for r, n in sorted(totals.items())) or "none"
    print(f"{sum(totals.values())} loads in {a.hours:g} h across {len(totals)} repos: {seen}")
    return 0


def cmd_compare(a: argparse.Namespace) -> int:
    db = resolve_db(a.db)
    if not db.is_file():
        print(f"no opencode.db at {db}")
        return 1
    csv_path = Path(a.csv) if a.csv else STATE_DIR / "adopted.csv"
    now = skill_now(a.skill, db, repo_dirs())
    if a.before:
        print(now)
        return 0
    before = skill_before(a.skill, csv_path)
    print(f"{a.skill}: before {before} now {now} {verdict_for(a.skill, before, now)}")
    return 0


def _token(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def board_open(tag: str, root: Path | None = None) -> int:
    root = root or HERE.parent
    try:
        text = (root / "sprint" / "board.md").read_text(encoding="utf-8")
    except OSError:
        return 0
    n = 0
    for line in text.splitlines():
        if line.startswith("|") and tag in line and ("| READY |" in line or "| DOING |" in line):
            n += 1
    return n


def compute_lanes(db: Path, root: Path | None = None) -> dict:
    root = root or HERE.parent
    dirs = repo_dirs()
    res = scan_db(db, 48, dirs) if db.is_file() else {"classes": {}, "families": {}}
    top = sorted(res["classes"].items(), key=lambda kv: -kv[1]["n"])
    top_id, top_n = (top[0][0], top[0][1]["n"]) if top else ("none", 0)
    rows = read_rows(STATE_DIR / "adopted.csv")
    flat = 0
    for i, r in enumerate(rows):
        if i == 0 or len(r) < 6 or r[3].strip().lower() != "adopted" or r[5].strip():
            continue
        flat += 1  # an adopted row still waiting for its after number is doctor work
    doctor_sig = f"{top_id}:{top_n}:waiting-{flat}"
    book_open = board_open("[BOOK]", root)
    book_sig = f"need-{book_open}" if book_open < 2 else "idle"
    try:
        ok, msg = fp.s6()
        proven = int(re.search(r"(\d+) of \d+ skills proven", msg).group(1)) if re.search(r"(\d+) of \d+ skills proven", msg) else 0
    except Exception:
        proven = 0
    pack_sig = f"ready-{proven}" if proven >= 3 else "idle"
    due = sum(1 for i, r in enumerate(rows) if i > 0 and len(r) >= 6 and r[3].strip().lower() == "adopted" and not r[5].strip())
    install_sig = f"work-{due}" if due else "idle"
    try:
        ph = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H", "--",
                             "book2skill", "mcp_server", "tools", "skills"],
                            capture_output=True, text=True, timeout=30).stdout.strip() or "none"
    except Exception:
        ph = "none"
    product_sig = ph[:8]
    try:
        inbox = (root / "sprint" / "inbox.md").read_text(encoding="utf-8")
        open_items = len(re.findall(r"^[-*] \[ \]", inbox, re.M))
    except OSError:
        open_items = 0
    planner_sig = _token(f"book{book_open}-inbox{open_items}-top{top_id}{top_n}")
    return {
        "doctor": {"signal": doctor_sig, "reason": f"top {top_id} {top_n} in 48 h, {flat} adopted rows wait"},
        "book": {"signal": book_sig, "reason": f"{book_open} open book rows"},
        "pack": {"signal": pack_sig, "reason": f"{proven} skills proven"},
        "install": {"signal": install_sig, "reason": f"{due} adopted rows wait for an after number"},
        "product": {"signal": product_sig, "reason": "last commit touching the product"},
        "planner": {"signal": planner_sig, "reason": f"{open_items} open inbox items"},
    }


def cmd_lanes(a: argparse.Namespace) -> int:
    db = resolve_db(a.db)
    lanes = compute_lanes(db)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    prev: dict = {}
    try:
        prev = json.loads((STATE_DIR / "lanes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev = {}
    out = {"generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}
    for lane, v in lanes.items():
        token = _token(v["signal"]) if lane != "product" else v["signal"]
        if lane == "product" and not re.fullmatch(r"[0-9a-f]{8}|none", token):
            token = _token(token)
        old = (prev.get(lane) or {}).get("token")
        out[lane] = {"token": old if old and (prev.get(lane) or {}).get("signal") == v["signal"] else token,
                     "reason": v["reason"], "signal": v["signal"]}
    (STATE_DIR / "lanes.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for lane, v in out.items():
        if lane == "generatedAt":
            continue
        print(f"{lane}: {v['token']} {v['reason']}")
    return 0


def round_numbers(db: Path, root: Path | None = None) -> dict:
    root = root or HERE.parent
    try:
        ok, msg = fp.s6()
        m = re.search(r"(\d+) of (\d+) skills proven", msg)
        proven = int(m.group(1)) if m else 0
    except Exception:
        proven = 0
    trials = len(list((root / "skills").glob("*/references/trial-proof.json"))) if (root / "skills").is_dir() else 0
    rows = read_rows(STATE_DIR / "adopted.csv")
    installed = sum(1 for i, r in enumerate(rows) if i > 0 and len(r) >= 4 and r[3].strip().lower() == "adopted")
    try:
        loads = fp.skill_loads(db, hours=24) if db.is_file() else {}
    except (sqlite3.Error, ValueError):
        loads = {}
    res = scan_db(db, 48, repo_dirs()) if db.is_file() else {"classes": {}}
    top = sorted(res["classes"].items(), key=lambda kv: -kv[1]["n"])
    top_id, top_n = (top[0][0], top[0][1]["n"]) if top else ("none", 0)
    try:
        text = (root / "sprint" / "steals.md").read_text(encoding="utf-8")
        tools = len(re.findall(r"\blanded\b", text))
    except OSError:
        tools = 0
    try:
        text = (root / "sprint" / "queue" / "checks.md").read_text(encoding="utf-8")
        n = len(re.findall(r"^ROUND \d+", text, re.M)) + 1
        last = [ln for ln in text.splitlines() if ln.startswith("ROUND ")]
        last_line = last[-1] if last else ""
    except OSError:
        n, last_line = 1, ""
    return {"n": n, "proven": proven, "trials": trials, "installed": installed,
            "loads": sum(loads.values()), "repos": len(loads), "class": top_id, "class_n": top_n,
            "tools": tools, "last": last_line}


def cmd_round(a: argparse.Namespace) -> int:
    db = resolve_db(a.db)
    cur = round_numbers(db)
    line = (f"ROUND {cur['n']} | proven {cur['proven']} | trials {cur['trials']} | installed {cur['installed']} | "
            f"loads 24h {cur['loads']} in {cur['repos']} repos | class {cur['class']} {cur['class_n']} | tools landed {cur['tools']}")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    prev: dict = {}
    try:
        prev = json.loads((STATE_DIR / "round.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev = {}
    same = all(prev.get(k) == cur[k] for k in ("proven", "trials", "installed", "loads", "repos", "class", "class_n", "tools"))
    print(line)
    if a.check and same and prev:
        return 1
    (STATE_DIR / "round.json").write_text(json.dumps({k: cur[k] for k in
        ("proven", "trials", "installed", "loads", "repos", "class", "class_n", "tools")}, indent=1), encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=None, help="opencode.db path (default OPENCODE_DB or the local share file)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan", help="top failure classes of the last hours; writes failures.json")
    p.add_argument("--hours", type=float, default=WINDOW_H)
    p.add_argument("--from", dest="from_", default=None, help="exact window start, ISO-8601 (overrides trailing --hours with --to)")
    p.add_argument("--to", default=None, help="exact window end, ISO-8601 (default now)")
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("loads", help="skill loads by skill and repo (shares one counter with S1/S2)")
    p.add_argument("--hours", type=float, default=24)
    p.set_defaults(fn=cmd_loads)
    p = sub.add_parser("compare", help="before and now for one skill; --before prints the 48 h count")
    p.add_argument("skill")
    p.add_argument("--before", action="store_true")
    p.add_argument("--csv", default=None)
    p.set_defaults(fn=cmd_compare)
    p = sub.add_parser("lanes", help="rewrite lane tokens; a token moves only when its lane has new work")
    p.set_defaults(fn=cmd_lanes)
    p = sub.add_parser("round-line", help="one ROUND line; --check exits 1 when no number moved")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_round)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
