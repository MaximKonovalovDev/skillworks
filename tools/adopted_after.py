"""The `after` numbers of the skill doctor's record, measured by themselves.

    python tools/adopted_after.py                 fill every due row of adopted.csv, print what happened
    python tools/adopted_after.py --status        say per row what it waits for; write nothing
    python tools/adopted_after.py --dry-run       measure and print; write nothing

adopted.csv (outside this public repo): `date,repo,skill,status,no_edit_before,no_edit_after`. The two numbers are the
repo's count, in 48 hours of the OpenCode history, of the failure class the skill targets (pwsh-for-bash-writers: pwsh
errors, git-one-branch: git errors and risky git commands, bash-spawn-guard: spawn kills (`ChildProcess.kill`) after
long foreground calls, bash-allowlist: policy denials (`prevents you from using this specific tool call`) after a pipe
or shell git reach; real-browser-automation and bevy-rust-ecs count USE and up is good, the other four count DOWN).
The classes are the ones center's skill-feed scan counted for the `before` column; the same definitions are
ported here so before and after compare.

A row is DUE 48 hours after its install. The install moment is the entry for the row's date in adopted-meta.json beside
the record (the time the before numbers were taken), else the end of that day (UTC). The `after` number is the count of
the last 48 hours, scaled to the shell calls of the before window (count x before shell calls / after shell calls), so a
loop that worked harder or less hard is compared by rate. It is written only when the repo's loop really ran through that
window: shell calls in at least 36 of the 48 hours, and at least half of the shell calls it made in the 48 hours before
the install (and at least 100). Without that rule a paused loop would count zero failures and every class would look
halved, and a few busy hours would pass for a full run. Until then the row stays empty and `--status` names the reason. `finish_proof.py s5` calls this when no halved class is on record yet, so the number is
filled while the bar is still open. after-log.jsonl beside the record keeps the raw count and the shell calls.

Meter reads are cached beside the record in after-scan-cache.json (install windows 7 days, the trailing 48 h
15 minutes), each store saved at once so a run killed at its timeout keeps what it measured. Fills still come
only from a fresh snapshot; the cache only answers guard checks and `waits` reasons fast.

The S1/S2 meter-read cache lives here too (cached_skill_loads, file loads-scan-cache.json): one 24 h
skill-loads scan of the multi-GB history costs minutes, past the proof budget, so the trailing-24 h
reading is reused 15 minutes (about 1% of the window). Counting is never reimplemented here: a miss
delegates to finish_proof.skill_loads, so the bar meaning cannot drift.

Needs the OpenCode database (read-only) and center's empire.json (repo name to folder), both read at run time.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import finish_proof as fp  # noqa: E402  (one place for the record path, the database path and which skills count use)

EMPIRE = Path(os.environ.get("EMPIRE_JSON") or "C:/Users/me/Desktop/center/empire.json")
WINDOW_H = 48
MIN_ACTIVITY = 0.5     # the after window needs this share of the before window's shell calls
MIN_SHELL = 100        # and at least this many shell calls
MIN_ACTIVE_HOURS = 36  # and shell calls in at least this many of the 48 hours: a full run, not a few busy hours

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_P_NOT_RECOGNIZED = re.compile(r"The term '([^']+)' is not recognized as a name of a cmdlet")
_P_PARSER = re.compile(r"ParserError|ParseException")
_P_DEVNULL = re.compile(r"Could not find a part of the path '?C:\\dev\\null", re.I)
_P_AMBIGUOUS_U = re.compile(r"parameter name 'u' is ambiguous")
_P_DATE_U = re.compile(r"\bdate\s+-u")
_P_FLAG_OUT = re.compile(r"(?:A parameter cannot be found that matches|Parameter cannot be processed because) (?:the )?parameter name '([a-zA-Z]{1,3})'")
_P_FLAG_CMD = re.compile(r"\b(ls|rm|cp|mv|cat|echo|sort|mkdir|head|tail|grep|date|diff|cd)\s+-[a-zA-Z]{1,3}\b")
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
# One entry per risky class; a class counts once per call however many of its patterns match (as center's scan bumped it).
_GIT_RISKY = [
    (re.compile(_C + r"add\s+(-A|--all|\.)(\s|$|;|\|)"),),
    (re.compile(_C + r"commit\b[^\n;|]*\s-[a-zA-Z]*a[a-zA-Z]*(\s|$)"), re.compile(r"\bgit\s+commit\b[^\n;|]*--all\b")),
    (re.compile(_C + r"commit\b[^\n;|]*--amend"),),
    (re.compile(_C + r"rebase\b"), re.compile(r"\bgit\s+pull\b[^\n;|]*--rebase(?!=false)")),
    (re.compile(_C + r"push\b[^\n;|]*(--force|\s-f(\s|$)|--force-with-lease)"),),
    (re.compile(_C + r"reset\s+--hard"),),
    (re.compile(_C + r"stash(\s+(push|save|pop|apply|drop|clear))?(\s|$|;|\|)"),),
    (re.compile(_C + r"checkout\s+(--\s|HEAD\s+--\s)"),),
    (re.compile(_C + r"restore\s+(?!--staged)"),),
    (re.compile(_C + r"clean\s+-[a-z]*f"),),
    (re.compile(_C + r"branch\s+-D\b"),),
]
_STASH_CLASS = 6
_GIT_STASH_READ = re.compile(r"\bgit\s+stash\s+(list|show)\b")
_BROWSER = re.compile(r"playwright|puppeteer|chromedriver|selenium|--remote-debugging|--headless|msedge|chrome\.exe|DevToolsActivePort", re.I)
_BEVY = re.compile(r"bevy", re.I)
_SPAWN_KILL = re.compile(r"ChildProcess\.kill")
_DENIED = re.compile(r"prevents you from using this specific tool call")

FAMILY = {"pwsh-for-bash-writers": "pwsh", "git-one-branch": "git", "real-browser-automation": "browser", "bevy-rust-ecs": "bevy",
          "bash-spawn-guard": "spawn", "bash-allowlist": "denied"}


def classify(tool: str, inp: dict, state: dict, repo: str) -> list[str]:
    """The target-class hits of one tool call, one family name per hit (a call can hit several classes of a family)."""
    hit: list[str] = []
    if repo == "engine2040" and _BEVY.search(json.dumps(inp, separators=(",", ":"), ensure_ascii=False)):
        hit.append("bevy")
    if tool != "bash":
        return hit
    out = state.get("output")
    if out is None:
        out = state.get("error")
    out = _ANSI.sub("", str(out if out is not None else ""))
    cmd = str(inp.get("command") or "")
    if _P_NOT_RECOGNIZED.search(out):
        hit.append("pwsh")
    if _P_PARSER.search(out):
        hit.append("pwsh")
    if _P_DEVNULL.search(out):
        hit.append("pwsh")
    if _P_AMBIGUOUS_U.search(out) and _P_DATE_U.search(cmd):
        hit.append("pwsh")
    elif _P_FLAG_OUT.search(out) and _P_FLAG_CMD.search(cmd):
        hit.append("pwsh")
    if _GIT_WORD.search(cmd):
        for rx_out, rx_cmd in _GIT_OUT:
            if rx_out.search(out) and (rx_cmd is None or rx_cmd.search(cmd)):
                hit.append("git")
        for n, alternatives in enumerate(_GIT_RISKY):
            if any(rx.search(cmd) for rx in alternatives) and not (n == _STASH_CLASS and _GIT_STASH_READ.search(cmd)):
                hit.append("git")
    if _BROWSER.search(cmd):
        hit.append("browser")
    if _SPAWN_KILL.search(out):
        hit.append("spawn")
    if _DENIED.search(out):
        hit.append("denied")
    return hit


def repo_dirs(path: Path = EMPIRE) -> list[tuple[str, str]]:
    doc = json.loads(path.read_text(encoding="utf-8-sig"))
    pairs = [(name, str(r["dir"]).replace("\\", "/").lower().rstrip("/")) for name, r in doc["repos"].items()]
    return sorted(pairs, key=lambda p: -len(p[1]))


def repo_of(directory: str | None, dirs: list[tuple[str, str]]) -> str:
    d = (directory or "").replace("\\", "/").lower().rstrip("/")
    for name, base in dirs:
        if d == base or d.startswith(base + "/"):
            return name
    return "other"


def _connect(db: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True, timeout=30)


def shell_activity(db: Path, dirs: list[tuple[str, str]], start_ms: float, end_ms: float) -> tuple[dict[str, int], dict[str, int]]:
    """Per repo, in the window (start, end]: the shell tool calls, and the number of hours (counted back from the end) that
    held at least one.

    Fast on a multi-GB history: the hour bucket is computed in SQLite and no
    `data` blob crosses into Python (only session ids and bucket numbers do);
    the counts are the same as grouping in SQL."""
    con = _connect(db)
    try:
        sess = {i: d for i, d in con.execute("select id, directory from session where time_updated > ?", (start_ms,))}
        calls: dict[str, int] = {}
        hours: dict[str, set[int]] = {}
        q = ("select session_id, cast((? - time_created) / 3600000 as integer) from part "
             "where time_created > ? and time_created <= ? "
             "and json_extract(data,'$.type')='tool' and json_extract(data,'$.tool')='bash'")
        for sid, hour in con.execute(q, (end_ms, start_ms, end_ms)):
            r = repo_of(sess.get(sid), dirs)
            calls[r] = calls.get(r, 0) + 1
            hours.setdefault(r, set()).add(hour)
        return calls, {r: len(h) for r, h in hours.items()}
    finally:
        con.close()


def shell_calls(db: Path, dirs: list[tuple[str, str]], start_ms: float, end_ms: float) -> dict[str, int]:
    """Shell tool calls per repo in the window (start, end]."""
    return shell_activity(db, dirs, start_ms, end_ms)[0]


# Slice widths for class_counts below: failure markers sit at the start of the
# error/output text (pwsh and git errors lead with the message), and the skill
# input names its command and file path up front. Widths stay bounded so one
# 48 h pass over a multi-GB history answers inside the 120 s proof budget.
_OUT_N = 400
_ERR_N = 400
_INP_N = 800


def class_counts(db: Path, dirs: list[tuple[str, str]], start_ms: float, end_ms: float) -> dict[str, dict[str, int]]:
    """{family: {repo: hits}} for the window (start, end]: every tool call, classified.

    Fast on a multi-GB history: SQLite hands over only the tool name, the full
    command and bounded slices of output, error and input (no full `data` blob
    crosses into Python, no json.loads per row). classify() sees the same
    fields with the same output-before-error preference; the bevy check also
    sees the input slice, since a read or edit names bevy in its file path
    rather than in a command."""
    con = _connect(db)
    try:
        sess = {i: d for i, d in con.execute("select id, directory from session where time_updated > ?", (start_ms,))}
        out: dict[str, dict[str, int]] = {fam: {} for fam in FAMILY.values()}
        q = ("select session_id, json_extract(data,'$.tool'), "
             "json_extract(data,'$.state.input.command'), "
             f"substr(json_extract(data,'$.state.output'),1,{_OUT_N}), "
             f"substr(json_extract(data,'$.state.error'),1,{_ERR_N}), "
             f"substr(json_extract(data,'$.state.input'),1,{_INP_N}) "
             "from part where time_created > ? and time_created <= ? "
             "and json_extract(data,'$.type')='tool'")
        for sid, tool, cmd, output, error, inp_json in con.execute(q, (start_ms, end_ms)):
            repo = repo_of(sess.get(sid), dirs)
            hits = classify(tool or "", {"command": cmd or ""}, {"output": output, "error": error}, repo)
            if repo == "engine2040" and "bevy" not in hits and _BEVY.search(inp_json or ""):
                hits = hits + ["bevy"]
            for fam in hits:
                out[fam][repo] = out[fam].get(repo, 0) + 1
        return out
    finally:
        con.close()


def read_rows(path: Path) -> list[list[str]]:
    return [r for r in csv.reader(path.read_text(encoding="utf-8-sig").splitlines()) if r]


def write_rows(path: Path, rows: list[list[str]]) -> None:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".adopted-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())
    os.replace(tmp, path)


def install_day_end(date: str) -> float | None:
    """End of the install day, UTC, in ms (the row only has a date, so the whole day counts as install time)."""
    try:
        d = datetime.strptime(date.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    except ValueError:
        return None
    return d.timestamp() * 1000


def load_meta(path: Path) -> dict[str, str]:
    """adopted-meta.json beside the record: {"<date>": "<ISO time>"}, the moment the before numbers were taken (right after
    the install). Without an entry the end of the install day is used."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        return {str(k): str(v) for k, v in doc.items()} if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def install_end(date: str, meta: dict[str, str]) -> float | None:
    if date.strip() in meta:
        try:
            return datetime.fromisoformat(meta[date.strip()].replace("Z", "+00:00")).timestamp() * 1000
        except ValueError:
            pass
    return install_day_end(date)


def verdict(skill: str, before: float, after: float) -> str:
    if skill in fp.UP_IS_GOOD:
        return "UP" if after > before else "FLAT" if after == before else "DOWN"
    if before > 0 and after * 2 <= before:
        return "HALVED"
    return "DOWN" if after < before else "FLAT" if after == before else "UP"


# Meter-read cache: one history scan of a multi-GB database costs a minute or more, and the S5 proof plus
# the arsenal `--status` tool share a 120 s budget. Install-window reads are history (they never move), so
# they are kept 7 days; trailing-48 h reads are reused 15 minutes (under 1% of the 48 h window) for guard
# checks and `waits` reasons. A row's `after` number is still filled only from a fresh, internally consistent
# snapshot (shell calls and class counts of the same window). The file sits beside adopted.csv and is replaced
# atomically; a missing or unreadable cache is a miss, never fatal. Each store saves at once, so a run killed
# at its timeout keeps what it measured and the next run finishes inside the budget.
CACHE_TTL_AFTER = 900
CACHE_TTL_BEFORE = 7 * 86400


def _load_cache(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_cache(path: Path, doc: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        before = doc.get("before")
        if isinstance(before, dict):
            keep = sorted(before, key=lambda k: before[k].get("at_ms", 0) if isinstance(before[k], dict) else 0)[-50:]
            doc = {**doc, "before": {k: before[k] for k in keep}}
        buf = json.dumps(doc)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".after-scan-cache-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(buf)
        os.replace(tmp, path)
    except OSError:
        pass  # a cache that cannot be written is skipped, never fatal


def _before_window(cache_file: Path | None, date: str, end: float, db: Path, dirs: list[tuple[str, str]],
                   now_ms: float) -> dict[str, int]:
    """Shell calls of one install window: history, so a cached reading is exact."""
    h = WINDOW_H * 3_600_000
    key = f"{date}|{datetime.fromtimestamp(end / 1000, timezone.utc):%Y-%m-%dT%H:%MZ}"
    if cache_file is not None:
        before = _load_cache(cache_file).get("before")
        hit = before.get(key) if isinstance(before, dict) else None
        if isinstance(hit, dict) and now_ms - hit.get("at_ms", 0) < CACHE_TTL_BEFORE * 1000 \
                and isinstance(hit.get("shell"), dict):
            return {k: int(v) for k, v in hit["shell"].items()}
    shell = shell_calls(db, dirs, end - h, end)
    if cache_file is not None:
        try:
            doc = _load_cache(cache_file)
            before = doc.get("before")
            if not isinstance(before, dict):
                before = {}
                doc["before"] = before
            before[key] = {"at_ms": now_ms, "shell": shell}
            _save_cache(cache_file, doc)
        except OSError:
            pass
    return shell


def _load_after(cache_file: Path | None, now_ms: float) -> dict | None:
    """The trailing-window snapshot when one is fresh enough, else None."""
    if cache_file is None:
        return None
    snap = _load_cache(cache_file).get("after")
    if not isinstance(snap, dict):
        return None
    if now_ms - snap.get("at_ms", 0) >= CACHE_TTL_AFTER * 1000:
        return None
    if not isinstance(snap.get("shell"), dict) or not isinstance(snap.get("hours"), dict):
        return None
    return snap


def _store_after(cache_file: Path | None, now_ms: float, calls: dict, hours: dict, classes: dict | None) -> None:
    if cache_file is None:
        return
    try:
        doc = _load_cache(cache_file)
        doc["after"] = {"at_ms": now_ms, "shell": calls, "hours": hours,
                        **({"classes": classes} if isinstance(classes, dict) else {})}
        _save_cache(cache_file, doc)
    except OSError:
        pass


# S1/S2 meter-read cache (shared home; finish_proof.py s1/s2 read it through cached_skill_loads).
# Same shape as the sibling's inline cache ({at_ms, db, loads}; hours/skills keys are only
# checked when present), so files written on either side stay readable on the other.
LOADS_CACHE = Path("C:/Users/me/.empire/state/skilldoctor/loads-scan-cache.json")
LOADS_TTL = 900


def _loads_hit(cache_file: Path | None, db_label: str, hours: float, names: list[str], now_ms: float,
               ttl: float = LOADS_TTL) -> dict[str, int] | None:
    """Fresh cached per-repo loads, else None (a missing or unreadable cache is a miss, never fatal)."""
    if cache_file is None:
        return None
    try:
        doc = json.loads(cache_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or not isinstance(doc.get("loads"), dict):
        return None
    try:
        at_ms = float(doc.get("at_ms", 0))
    except (TypeError, ValueError):
        return None
    if now_ms - at_ms >= ttl * 1000:
        return None
    if doc.get("db") != db_label:
        return None
    if "hours" in doc and doc["hours"] != hours:
        return None
    if "skills" in doc and sorted(doc["skills"]) != sorted(names):
        return None
    try:
        return {str(r): int(n) for r, n in doc["loads"].items()}
    except (TypeError, ValueError):
        return None


def _loads_store(cache_file: Path | None, db_label: str, hours: float, names: list[str],
                 loads: dict[str, int], now_ms: float) -> None:
    """Save one reading at once (a cache that cannot be written is skipped, never fatal)."""
    if cache_file is None:
        return
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {"at_ms": now_ms, "db": db_label, "hours": hours, "skills": sorted(names),
                   "loads": {str(r): int(n) for r, n in loads.items()}}
        fd, tmp = tempfile.mkstemp(dir=str(cache_file.parent), prefix=".loads-scan-cache-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(payload))
        os.replace(tmp, cache_file)
    except (OSError, ValueError):
        pass


def cached_skill_loads(db: Path | None = None, *, hours: float | None = None, now_ms: float | None = None,
                       skills: Path | None = None, own: Path | None = None,
                       cache_file: Path | None = None, ttl: float = LOADS_TTL) -> tuple[dict[str, int] | None, bool]:
    """Per-repo loads of this repo's skills for the S1/S2 breadth path: cached meter reads when
    fresh, else one database scan (so the second proof run answers from the cache).

    The bar meaning is unchanged: counting always delegates to finish_proof.skill_loads (a `skill`
    tool call naming a skill of this repo, in a session that ran in another repo). The default
    database (db=None) answers from the default cache file; a file given on the command line or
    by a test is read as it is, never from the cache (pass an explicit cache_file to cache it,
    as tests do). Returns (loads, from_cache); loads is None when the database file is missing."""
    path = fp._db_path(db)
    if not path.is_file():
        return None, False
    cache = LOADS_CACHE if (cache_file is None and db is None) else cache_file
    now = time.time() * 1000 if now_ms is None else now_ms
    h = fp.HOURS if hours is None else hours
    names = sorted(fp._skill_names(skills or fp.SKILLS))
    if cache is not None:
        hit = _loads_hit(cache, str(path), h, names, now, ttl)
        if hit is not None:
            return hit, True
    loads = fp.skill_loads(path, hours=h, now_ms=now, skills=skills, own=own)
    if cache is not None:
        _loads_store(cache, str(path), h, names, loads, now)
    return loads, False


def plan(rows: list[list[str]], now_ms: float, db: Path, dirs: list[tuple[str, str]], meta: dict[str, str] | None = None,
         cache_file: Path | None = None) -> list[dict]:
    """One entry per adopted row without an after number: due or not, and when due the number or the reason it waits.

    The number is the raw count of the last 48 hours scaled to the shell calls of the before window (count x before shell
    calls / after shell calls), so a loop that worked twice as hard or half as hard is compared by rate, as center's
    compare does per 1000 shell calls. Pass `cache_file` (beside adopted.csv) to reuse meter reads within their TTL;
    without it every number is scanned fresh."""
    meta = meta or {}
    h = WINDOW_H * 3_600_000
    before_shell: dict[str, dict[str, int]] = {}
    after: dict = {}
    items = []
    for i, r in enumerate(rows):
        if i == 0 or len(r) < 6 or r[3].strip().lower() != "adopted" or r[5].strip():
            continue
        date, repo, skill = r[0].strip(), r[1].strip(), r[2].strip()
        item = {"row": i, "date": date, "repo": repo, "skill": skill, "due": False, "value": None, "why": ""}
        items.append(item)
        end = install_end(date, meta)
        if end is None or skill not in FAMILY:
            item["why"] = "unreadable date or unknown skill"
            continue
        if now_ms < end + h:
            item["why"] = f"not due: 48 hours after the install ({datetime.fromtimestamp(end / 1000, timezone.utc):%Y-%m-%d %H:%MZ}) is {datetime.fromtimestamp((end + h) / 1000, timezone.utc):%Y-%m-%d %H:%MZ}"
            continue
        item["due"] = True
        if date not in before_shell:
            before_shell[date] = _before_window(cache_file, date, end, db, dirs, now_ms)
        if "shell" not in after:
            snap = _load_after(cache_file, now_ms)
            if snap is None:
                calls, hours = shell_activity(db, dirs, now_ms - h, now_ms)
                _store_after(cache_file, now_ms, calls, hours, None)
                after["shell"] = (calls, hours)
                after["snap"] = "fresh"
            else:
                after["shell"] = ({k: int(v) for k, v in snap["shell"].items()},
                                  {k: int(v) for k, v in snap["hours"].items()})
                after["snap"] = "cache"
                after["snap_classes"] = snap.get("classes") if isinstance(snap.get("classes"), dict) else None
        b, a, active = before_shell[date].get(repo, 0), after["shell"][0].get(repo, 0), after["shell"][1].get(repo, 0)
        need = max(MIN_SHELL, MIN_ACTIVITY * b)
        item.update(before_shell=b, after_shell=a, active_hours=active)
        if active < MIN_ACTIVE_HOURS:
            item["why"] = (f"waits: {repo} ran in {active} of the last {WINDOW_H} hours, needs {MIN_ACTIVE_HOURS}; "
                           f"the loop was paused or idle, so its count would not be a full {WINDOW_H} hours")
            continue
        if a < need:
            item["why"] = (f"waits: {repo} made {a} shell calls in the last {WINDOW_H} h, needs {need:.0f} "
                           f"({int(MIN_ACTIVITY * 100)}% of the {b} before, at least {MIN_SHELL}); the loop was idle")
            continue
        if "classes" not in after:
            if after.get("snap") == "cache" and isinstance(after.get("snap_classes"), dict):
                after["classes"] = after["snap_classes"]
            else:
                # Fills come only from a fresh, internally consistent snapshot: shell calls and class
                # counts of the same window, so the permanent record never holds mixed-window numbers.
                calls, hours = shell_activity(db, dirs, now_ms - h, now_ms)
                after["shell"] = (calls, hours)
                after["classes"] = class_counts(db, dirs, now_ms - h, now_ms)
                after["snap"] = "fresh"
                _store_after(cache_file, now_ms, calls, hours, after["classes"])
                b, a, active = before_shell[date].get(repo, 0), calls.get(repo, 0), hours.get(repo, 0)
                item.update(before_shell=b, after_shell=a, active_hours=active)
                need = max(MIN_SHELL, MIN_ACTIVITY * b)
                if active < MIN_ACTIVE_HOURS:
                    item["value"] = None
                    item["why"] = (f"waits: {repo} ran in {active} of the last {WINDOW_H} hours, needs {MIN_ACTIVE_HOURS}; "
                                   f"the loop was paused or idle, so its count would not be a full {WINDOW_H} hours")
                    continue
                if a < need:
                    item["value"] = None
                    item["why"] = (f"waits: {repo} made {a} shell calls in the last {WINDOW_H} h, needs {need:.0f} "
                                   f"({int(MIN_ACTIVITY * 100)}% of the {b} before, at least {MIN_SHELL}); the loop was idle")
                    continue
        raw = after["classes"][FAMILY[skill]].get(repo, 0)
        item["raw"] = raw
        item["value"] = round(raw * b / a) if b else raw
    return items


def refresh(path: Path, db: Path | None = None, empire: Path | None = None, now_ms: float | None = None, dry_run: bool = False,
            log: Path | None = None) -> tuple[list[dict], str]:
    """Fill every due row whose window is comparable. Returns (plan items, one summary line)."""
    db = db or fp._db_path(None)
    rows = read_rows(path)
    if not rows or [c.strip() for c in rows[0]][:2] != ["date", "repo"]:
        return [], "no usable adopted.csv"
    if not db.is_file():
        return [], f"no opencode.db at {db}"
    now_ms = time.time() * 1000 if now_ms is None else now_ms
    items = plan(rows, now_ms, db, repo_dirs(empire or EMPIRE), load_meta(path.parent / "adopted-meta.json"),
                 path.parent / "after-scan-cache.json")
    filled = [it for it in items if it["value"] is not None]
    for it in filled:
        it["verdict"] = verdict(it["skill"], float(rows[it["row"]][4] or 0), float(it["value"]))
    if filled and not dry_run:
        for it in filled:
            rows[it["row"]][5] = str(it["value"])
        write_rows(path, rows)
        if log is not None:
            at = datetime.fromtimestamp(now_ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            with log.open("a", encoding="utf-8") as fh:
                for it in filled:
                    fh.write(json.dumps({"at": at, **{k: it[k] for k in ("date", "repo", "skill", "raw", "value", "verdict", "before_shell", "after_shell", "active_hours")}}) + "\n")
    due = sum(1 for it in items if it["due"])
    return items, f"{len(filled)} after numbers {'would be ' if dry_run else ''}filled, {due - len(filled)} due rows wait for a comparable window, {len(items) - due} not due yet"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=str(fp.ADOPTED))
    ap.add_argument("--db", default=None)
    ap.add_argument("--empire", default=None)
    ap.add_argument("--now", default=None, help="ISO time to measure at, for checking (default now)")
    ap.add_argument("--status", action="store_true", help="say per row what it waits for; write nothing")
    ap.add_argument("--dry-run", action="store_true", help="measure and print; write nothing")
    args = ap.parse_args(argv)
    now_ms = datetime.fromisoformat(args.now.replace("Z", "+00:00")).timestamp() * 1000 if args.now else None
    path = Path(args.csv)
    items, summary = refresh(path, Path(args.db) if args.db else None, Path(args.empire) if args.empire else None, now_ms,
                             dry_run=args.status or args.dry_run, log=path.parent / "after-log.jsonl")
    for it in items:
        what = f"-> {it['value']} {it.get('verdict', '')}".strip() if it["value"] is not None else it["why"]
        print(f"{it['date']} {it['repo']:<17} {it['skill']:<26} {what}")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
