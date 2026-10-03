"""real-browser-automation: the loopback guard, the CLI, and a real Edge/Chrome driven over CDP.

Fast tests (no browser) always run. The tests that start a browser are `live`: they run with
SKILL_LIVE=1 (python tests/live_proof.py real-browser-automation) and skip with a clear reason
when Node 22+ or an installed Edge/Chrome is missing. They talk to a server on 127.0.0.1 only.
"""
import functools
import json
import re
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

SKILL = g.SKILLS / "real-browser-automation"
SCRIPT = SKILL / "scripts" / "cdp.mjs"
LIB_URL = SCRIPT.as_uri()
NODE = shutil.which("node")

pytestmark = [
    pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet"),
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


def node_module(code: str, *args: str, timeout: int = 20) -> subprocess.CompletedProcess:
    """Run an inline ES module; extra args arrive as process.argv.slice(1)."""
    return subprocess.run([NODE, "--input-type=module", "-e", code, *args], capture_output=True, text=True, timeout=timeout)


def cli(*args: str, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run([NODE, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- fast tests, no browser

ALLOWED = [
    "http://127.0.0.1:8080/",
    "https://127.0.0.1/",
    "http://localhost:3000/a?b=1",
    "HTTP://LOCALHOST/",
    "ws://127.0.0.1:9229/x",
    "wss://localhost/x",
    "http://[::1]:8080/",
    "http://app.localhost:8080/",
    "http://a.b.localhost/",
]
REFUSED = [
    "http://example.com/",
    "https://www.example.com/",
    "http://127.0.0.1.evil.com/",
    "http://localhost.evil.com/",
    "http://127.0.0.1@evil.com/",
    "http://evil.com/?h=127.0.0.1",
    "http://evil.com/#localhost",
    "http://10.0.0.1/",
    "http://192.168.1.5/",
    "http://127.0.0.2/",
    "http://0.0.0.0/",
    "http://[::ffff:7f00:1]/",
    "http://localhost./",
    "http://.localhost/",
    "ftp://127.0.0.1/",
    "data:text/html,hi",
    "file:///C:/Windows/win.ini",
    "about:blank",
    "chrome://version",
    "javascript:alert(1)",
    "blob:http://127.0.0.1/abc",
    "not a url",
    "",
]

GUARD_JS = """
const [libUrl, listJson] = process.argv.slice(1);
const m = await import(libUrl);
const urls = JSON.parse(listJson);
const out = {};
for (const u of urls) {
  let verdict = 'allow';
  try { m.assertLocal(u); } catch (e) { verdict = e.name === 'LocalOnlyError' ? 'refuse' : 'other:' + e.name; }
  out[u] = { assertLocal: verdict, isLocalUrl: m.isLocalUrl(u) };
}
console.log(JSON.stringify(out));
"""


def test_guard_allows_only_loopback_hosts() -> None:
    r = node_module(GUARD_JS, LIB_URL, json.dumps(ALLOWED + REFUSED))
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    for u in ALLOWED:
        assert got[u]["assertLocal"] == "allow" and got[u]["isLocalUrl"] is True, f"should be allowed: {u}"
    for u in REFUSED:
        assert got[u]["assertLocal"] == "refuse" and got[u]["isLocalUrl"] is False, f"should be refused: {u!r} -> {got[u]}"


def test_user_info_trick_is_judged_by_the_real_host() -> None:
    r = node_module(GUARD_JS, LIB_URL, json.dumps(["http://evil.com%2F@127.0.0.1/", "http://127.0.0.1:80@evil.com/"]))
    got = json.loads(r.stdout)
    assert got["http://evil.com%2F@127.0.0.1/"]["assertLocal"] == "allow"   # host is 127.0.0.1
    assert got["http://127.0.0.1:80@evil.com/"]["assertLocal"] == "refuse"  # host is evil.com


WHITELIST_JS = """
const [libUrl] = process.argv.slice(1);
const m = await import(libUrl);
const t = (u, allow) => { try { m.assertLocal(u, { allow }); return 'allow'; } catch (e) { return 'refuse'; } };
console.log(JSON.stringify({
  dataPlain: t('data:text/html,hi', []),
  dataWhitelisted: t('data:text/html,hi', ['data:']),
  fileWhitelisted: t('file:///C:/x.html', ['file:']),
  aboutBlankExact: t('about:blank', ['about:blank']),
  hostNotOpenedByDataEntry: t('http://example.com/', ['data:']),
  hostNotOpenedByHttpEntry: t('http://example.com/', ['http:']),
  hostNotOpenedByExactEntry: t('http://example.com/', ['http://example.com/']),
  pageRequests: {
    data: m.requestAllowed('data:text/plain,x'), blob: m.requestAllowed('blob:http://127.0.0.1/u'), about: m.requestAllowed('about:blank'),
    file: m.requestAllowed('file:///C:/x'), foreign: m.requestAllowed('http://blocked.invalid/x'), local: m.requestAllowed('http://127.0.0.1:1/x'),
  },
}));
"""


def test_whitelist_opens_non_network_schemes_but_never_a_host() -> None:
    r = node_module(WHITELIST_JS, LIB_URL)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    assert got["dataPlain"] == "refuse"
    assert got["dataWhitelisted"] == "allow"
    assert got["fileWhitelisted"] == "allow"
    assert got["aboutBlankExact"] == "allow"
    assert got["hostNotOpenedByDataEntry"] == "refuse"
    assert got["hostNotOpenedByHttpEntry"] == "refuse"
    assert got["hostNotOpenedByExactEntry"] == "refuse"
    assert got["pageRequests"] == {"data": True, "blob": True, "about": True, "file": False, "foreign": False, "local": True}


def test_cli_check_url_needs_no_browser() -> None:
    ok = cli("--check-url", "http://localhost:3000/")
    assert ok.returncode == 0 and ok.stdout.startswith("ALLOW ")
    bad = cli("--check-url", "http://example.com/")
    assert bad.returncode == 3 and bad.stdout.startswith("REFUSE ")
    data = cli("--check-url", "data:text/html,hi")
    assert data.returncode == 3
    data_ok = cli("--check-url", "data:text/html,hi", "--allow", "data:")
    assert data_ok.returncode == 0


def test_cli_refuses_a_foreign_url_before_starting_any_browser() -> None:
    r = cli("--url", "http://example.com/", "--eval", "1")
    assert r.returncode == 3
    assert "not 127.0.0.1" in r.stderr
    assert r.stdout.strip() == ""  # no result object: nothing ran


FORBIDDEN_JS = """
const [libUrl] = process.argv.slice(1);
const m = await import(libUrl);
const t = async o => { try { await m.launch(o); return 'started'; } catch (e) { return e.message; } };
console.log(JSON.stringify({
  addr: await t({ args: ['--remote-debugging-address=0.0.0.0'] }),
  proxy: await t({ args: ['--proxy-server=http://example.com:3128'] }),
  rules: await t({ args: ['--host-resolver-rules=MAP * 1.2.3.4'] }),
  origins: await t({ args: ['--remote-allow-origins=*'] }),
  allowHttp: await t({ allow: ['http://example.com/'] }),
}));
"""


def test_launch_refuses_flags_that_open_the_network_before_spawning() -> None:
    r = node_module(FORBIDDEN_JS, LIB_URL)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    for key in ("addr", "proxy", "rules", "origins"):
        assert "launch arg not allowed" in got[key], got
    assert "allow cannot admit" in got["allowHttp"], got


def test_keyboard_table_gives_real_key_descriptions() -> None:
    js = """
    const m = await import(process.argv[1]);
    console.log(JSON.stringify([m.keyFor('a'), m.keyFor('A'), m.keyFor('7'), m.keyFor('@'), m.keyFor('Enter'), m.keyFor('\\u05d0')]));
    """
    r = node_module(js, LIB_URL)
    a, upper, seven, at, enter, hebrew = json.loads(r.stdout)
    assert (a["code"], a["vk"], a["modifiers"]) == ("KeyA", 65, 0)
    assert (upper["code"], upper["vk"], upper["modifiers"]) == ("KeyA", 65, 8)   # Shift is bit 8
    assert (seven["code"], seven["vk"]) == ("Digit7", 55)
    assert (at["code"], at["modifiers"]) == ("Digit2", 8)
    assert (enter["key"], enter["vk"]) == ("Enter", 13)
    assert hebrew is None  # no US key: the script falls back to Input.insertText


def test_script_never_kills_a_process() -> None:
    code = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"\.kill\(|taskkill|Stop-Process|SIGKILL|SIGTERM|process\.exit\(", code), "cdp.mjs must not kill anything"
    assert "'Browser.close'" in code
    assert "'--remote-debugging-address'" in code  # only ever as an entry of the refused-flags list
    assert "--remote-debugging-address=" not in code


# ---------------------------------------------------------------- live tests: a real browser

class Site:
    """A page on 127.0.0.1 that sends a beacon like a bot-detection target would."""

    PAGE = b"""<!doctype html><title>beacon test</title>
<input id="name"><button id="go">go</button><p id="out"></p>
<script>
window.log = [];
const n = document.getElementById('name');
n.addEventListener('keydown', e => log.push(['keydown', e.key, e.isTrusted]));
document.getElementById('go').addEventListener('click', e => {
  log.push(['click', e.isTrusted]);
  document.getElementById('out').textContent = 'hello ' + n.value;
});
fetch('/beacon', { method: 'POST', headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ ua: navigator.userAgent, webdriver: navigator.webdriver }) }).then(() => { window.beaconDone = true; });
</script>"""

    def __init__(self) -> None:
        site = self
        self.beacons: list[dict] = []
        self.paths: list[str] = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a) -> None:  # silence
                pass

            def do_GET(self) -> None:
                site.paths.append(self.path)
                if self.path == "/redir":
                    self.send_response(302)
                    self.send_header("Location", "http://redirect-blocked.invalid/x")
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(site.PAGE)))
                self.end_headers()
                self.wfile.write(site.PAGE)

            def do_POST(self) -> None:
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                if self.path == "/beacon":
                    site.beacons.append(json.loads(body))
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"ok")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> "Site":
        self.thread.start()
        return self

    def __exit__(self, *a) -> None:
        self.server.shutdown()
        self.server.server_close()


@functools.lru_cache(maxsize=1)
def installed_browsers() -> dict:
    """Which of Edge and Chrome the script finds, via its own --info (empty when node is too old or none is installed)."""
    out = {}
    if NODE is None or not SCRIPT.is_file():
        return out
    ver = subprocess.run([NODE, "--version"], capture_output=True, text=True).stdout.strip().lstrip("v").split(".")[0]
    if not ver.isdigit() or int(ver) < 22:
        return out
    for name in ("edge", "chrome"):
        r = cli("--info", "--browser", name)
        if r.returncode == 0 and r.stdout.strip() not in ("", "null"):
            out[name] = json.loads(r.stdout)["path"]
    return out


def need_browser(which: str = "") -> None:
    """Skip with a clear reason when Node 22+ or the wanted installed browser is missing."""
    found = installed_browsers()
    if not found:
        pytest.skip("needs Node 22+ and an installed Edge or Chrome (`cdp.mjs --info` found none)")
    if which and which not in found:
        pytest.skip(f"{which} is not installed")


def pid_alive(pid: int) -> bool:
    """Look only; never touches the process."""
    if sys.platform == "win32":
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"], capture_output=True, text=True)
        return f'"{pid}"' in r.stdout
    return subprocess.run(["ps", "-p", str(pid), "-o", "pid="], capture_output=True, text=True).returncode == 0


FLOW_JS = """
const [libUrl, base, which, shot] = process.argv.slice(1);
const m = await import(libUrl);
const out = {};
// --disable-gpu only makes close() fast on a busy PC; the logic under test is the same.
const browser = await m.launch({ browser: which, args: ['--disable-gpu'], closeTimeout: 60000 });
out.pid = browser.pid; out.profile = browser.userDataDir; out.product = browser.product;
try {
  const page = await browser.newPage();
  await page.goto(base + '/');
  await page.waitForFunction('window.beaconDone === true');
  out.ua = await page.evaluate('navigator.userAgent');
  out.webdriver = await page.evaluate('navigator.webdriver');
  await page.type('#name', 'Ada');
  await page.click('#go');
  out.hello = await page.evaluate("document.getElementById('out').textContent");
  out.log = await page.evaluate('window.log');
  out.shot = await page.screenshot(shot);
  // a foreign navigation is refused before any request
  try { await page.goto('http://example.com/'); out.refused = 'NOT REFUSED'; } catch (e) { out.refused = e.name; }
  out.blockedAfterRefusal = browser.blocked.length;
  // a request the loaded page makes itself is blocked by the Fetch guard
  await page.goto(base + '/');
  out.fetchResult = await page.evaluate("fetch('http://blocked.invalid/x').then(() => 'loaded', () => 'failed')");
  out.blocked = browser.blocked.map(b => b.url);
  // a redirect from loopback to a foreign host is blocked on the second hop
  out.redirect = await page.goto(base + '/redir').then(() => 'loaded', e => e.message);
  out.blockedAfterRedirect = browser.blocked.map(b => b.url);
  // *.localhost is loopback
  await page.goto(base.replace('127.0.0.1', 'test.localhost') + '/');
  out.localhostTitle = await page.evaluate('document.title');
} finally {
  await browser.close();
}
out.profileRemoved = browser.profileRemoved;
console.log(JSON.stringify(out));
"""


@live
@pytest.mark.parametrize("which", ["edge", "chrome"])
def test_real_browser_beacon_guard_and_clean_close(which: str, tmp_path: Path) -> None:
    need_browser(which)
    shot = tmp_path / "shot.png"
    with Site() as site:
        r = node_module(FLOW_JS, LIB_URL, f"http://127.0.0.1:{site.port}", which, str(shot), timeout=100)
        assert r.returncode == 0, r.stderr[-1500:]
        out = json.loads(r.stdout.strip().splitlines()[-1])

        # the browser itself produced the beacon, and it equals what evaluate() saw
        assert len(site.beacons) >= 1
        assert site.beacons[0]["ua"] == out["ua"]
        assert site.beacons[0]["webdriver"] == out["webdriver"]
        assert isinstance(out["webdriver"], bool)
        assert "Chrome/" in out["ua"]

        # real input events reached the page, trusted
        assert out["hello"] == "hello Ada"
        keydowns = [e for e in out["log"] if e[0] == "keydown"]
        assert [e[1] for e in keydowns] == ["A", "d", "a"] and all(e[2] is True for e in keydowns)
        assert ["click", True] in out["log"]
        assert shot.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

        # guard: foreign navigation refused with no request, page fetch blocked, redirect hop blocked
        assert out["refused"] == "LocalOnlyError"
        assert out["blockedAfterRefusal"] == 0
        assert out["fetchResult"] == "failed"
        assert out["blocked"] == ["http://blocked.invalid/x"]
        assert "ERR_BLOCKED_BY_CLIENT" in out["redirect"]
        assert out["blockedAfterRedirect"] == ["http://blocked.invalid/x", "http://redirect-blocked.invalid/x"]
        assert out["localhostTitle"] == "beacon test"

        # closed through Browser.close: the process is gone and the temp profile was removed
        assert not pid_alive(out["pid"]), f"browser pid {out['pid']} still running after close()"
        assert out["profileRemoved"] is True
        assert not Path(out["profile"]).exists()


@live
def test_cli_example_from_the_skill(tmp_path: Path) -> None:
    need_browser()
    shot = tmp_path / "out.png"
    with Site() as site:
        r = cli("--url", f"http://127.0.0.1:{site.port}/", "--wait-for", "#go", "--type", "#name=Ada", "--click", "#go",
                "--eval", "navigator.webdriver", "--eval", "document.getElementById('out').textContent",
                "--screenshot", str(shot), "--arg", "--disable-gpu", timeout=100)
        assert r.returncode == 0, (r.stdout + r.stderr)[-1500:]
        out = json.loads(r.stdout)
        assert out["closed"] is True and out["blockedRequests"] == []
        assert out["eval"][1] == "hello Ada"
        assert isinstance(out["eval"][0], bool)
        assert shot.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert site.beacons and site.beacons[0]["webdriver"] == out["eval"][0]
