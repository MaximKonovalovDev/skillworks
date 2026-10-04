"""The `after` numbers of the skill doctor's record, measured by themselves.

    python tools/adopted_after.py                 fill every due row of adopted.csv, print what happened
    python tools/adopted_after.py --status        say per row what it waits for; write nothing
    python tools/adopted_after.py --dry-run       measure and print; write nothing

adopted.csv (outside this public repo): `date,repo,skill,status,no_edit_before,no_edit_after`. The two numbers are the
repo's count, in 48 hours of the OpenCode history, of the failure class the skill targets (pwsh-for-bash-writers: pwsh
errors, git-one-branch: git errors and risky git commands; real-browser-automation and bevy-rust-ecs count USE and up is
good). The classes are the ones center's skill-feed scan counted for the `before` column; the same definitions are
ported here so before and after compare.

A row is DUE 48 hours after its install. The install moment is the entry for the row's date in adopted-meta.json beside
the record (the time the before numbers were taken), else the end of that day (UTC). The `after` number is the count of
the last 48 hours, scaled to the shell calls of the before window (count x before shell calls / after shell calls), so a
loop that worked harder or less hard is compared by rate. It is written only when the repo's loop really ran through that
window: shell calls in at least 36 of the 48 hours, and at least half of the shell calls it made in the 48 hours before
the install (and at least 100). Without that rule a paused loop would count zero failures and every class would look
halved, and a few busy hours would pass for a full run. Until then the row stays empty and `--status` names the reason. `finish_proof.py s5` calls this before it reads the file, so the number is
filled whenever the finish line is measured. after-log.jsonl beside the record keeps the raw count and the shell calls.

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

FAMILY = {"pwsh-for-bash-writers": "pwsh", "git-one-branch": "git", "real-browser-automation": "browser", "bevy-rust-ecs": "bevy"}


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
    held at least one."""
    con = _connect(db)
    try:
        sess = {i: d for i, d in con.execute("select id, directory from session where time_updated > ?", (start_ms,))}
        calls: dict[str, int] = {}
        hours: dict[str, set[int]] = {}
        q = ("select session_id, cast((? - time_created) / 3600000 as integer), count(*) from part "
             "where time_created > ? and time_created <= ? and json_extract(data,'$.type')='tool' and json_extract(data,'$.tool')='bash' "
             "group by session_id, 2")
        for sid, hour, n in con.execute(q, (end_ms, start_ms, end_ms)):
            r = repo_of(sess.get(sid), dirs)
            calls[r] = calls.get(r, 0) + n
            hours.setdefault(r, set()).add(hour)
        return calls, {r: len(h) for r, h in hours.items()}
    finally:
        con.close()


def shell_calls(db: Path, dirs: list[tuple[str, str]], start_ms: float, end_ms: float) -> dict[str, int]:
    """Shell tool calls per repo in the window (start, end]."""
    return shell_activity(db, dirs, start_ms, end_ms)[0]


def class_counts(db: Path, dirs: list[tuple[str, str]], start_ms: float, end_ms: float) -> dict[str, dict[str, int]]:
    """{family: {repo: hits}} for the window (start, end]: every tool call, classified."""
    con = _connect(db)
    try:
        sess = {i: d for i, d in con.execute("select id, directory from session where time_updated > ?", (start_ms,))}
        out: dict[str, dict[str, int]] = {"pwsh": {}, "git": {}, "browser": {}, "bevy": {}}
        q = "select session_id, data from part where time_created > ? and time_created <= ? and json_extract(data,'$.type')='tool'"
        for sid, data in con.execute(q, (start_ms, end_ms)):
            try:
                part = json.loads(data)
            except ValueError:
                continue
            state = part.get("state") or {}
            repo = repo_of(sess.get(sid), dirs)
            for fam in classify(part.get("tool") or "", state.get("input") or {}, state, repo):
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


def plan(rows: list[list[str]], now_ms: float, db: Path, dirs: list[tuple[str, str]], meta: dict[str, str] | None = None) -> list[dict]:
    """One entry per adopted row without an after number: due or not, and when due the number or the reason it waits.

    The number is the raw count of the last 48 hours scaled to the shell calls of the before window (count x before shell
    calls / after shell calls), so a loop that worked twice as hard or half as hard is compared by rate, as center's
    compare does per 1000 shell calls."""
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
            before_shell[date] = shell_calls(db, dirs, end - h, end)
        if "shell" not in after:
            after["shell"] = shell_activity(db, dirs, now_ms - h, now_ms)
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
            after["classes"] = class_counts(db, dirs, now_ms - h, now_ms)
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
    items = plan(rows, now_ms, db, repo_dirs(empire or EMPIRE), load_meta(path.parent / "adopted-meta.json"))
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
