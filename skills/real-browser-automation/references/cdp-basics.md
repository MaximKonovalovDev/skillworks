# CDP basics: what scripts/cdp.mjs sends

Protocol source: ChromeDevTools/devtools-protocol, commit `d209a9a38897d2935a078a0bf00ca821811d21ed`
(master, 2026-10-03), protocol version 1.3. Methods and events of `Runtime` live in `json/js_protocol.json`;
all other domains below are in `json/browser_protocol.json`. Verified 2026-10-03: a scan of every
`Domain.name` string in `scripts/cdp.mjs` found 24 names, 0 missing, and the parameter names listed below
all exist in the JSON. Items marked "observed" are browser behaviour that is not in the protocol JSON.

## 1. Start the browser and find the port (no npm)

Flags: `--headless=new --remote-debugging-port=0 --user-data-dir=<fresh temp dir> --no-first-run
--no-default-browser-check`. Port 0 means "browser picks a free port". The browser then writes the file
`DevToolsActivePort` into the profile dir: line 1 is the port, line 2 is the browser WebSocket path
(`/devtools/browser/<uuid>`). Connect to `ws://127.0.0.1:<port><path>`. Observed on Edge 154 and Chrome 154:
- Reading that file at the wrong moment can fail with EBUSY: retry the read.
- `http://127.0.0.1:<port>/json/version` answers with keys Browser, Protocol-Version, User-Agent,
  V8-Version, WebKit-Version, webSocketDebuggerUrl.
- Chrome prints `DevTools listening on ws://...` on stderr; Edge printed nothing there.
- Never pass `--remote-debugging-address`: the default already listens on 127.0.0.1 only.

Smallest complete example, raw, tested on Edge 154 (no guard in this version, use scripts/cdp.mjs for real work):

```js
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const exe = join(process.env['ProgramFiles(x86)'], 'Microsoft', 'Edge', 'Application', 'msedge.exe');
const dir = mkdtempSync(join(tmpdir(), 'raw-profile-'));
spawn(exe, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${dir}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
let lines = [];
while (lines.length < 2) {
  await new Promise(r => setTimeout(r, 50));
  try { lines = readFileSync(join(dir, 'DevToolsActivePort'), 'utf8').split(/\r?\n/).filter(Boolean); } catch {}
}
const ws = new WebSocket(`ws://127.0.0.1:${lines[0]}${lines[1]}`);
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const waiting = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id) waiting.get(m.id)(m); });
const send = (method, params = {}, sessionId) =>
  new Promise(res => { waiting.set(++id, res); ws.send(JSON.stringify({ id, method, params, sessionId })); });
const { result: { targetId } } = await send('Target.createTarget', { url: 'about:blank' });
const { result: { sessionId } } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, sessionId);
await send('Page.navigate', { url: 'http://127.0.0.1:8080/' }, sessionId); // real code waits for Page.loadEventFired
const r = await send('Runtime.evaluate', { expression: 'navigator.webdriver', returnByValue: true }, sessionId);
console.log(r.result.result.value);
await send('Browser.close');   // then delete the temp profile dir yourself
```

`Target.attachToTarget` (params targetId, flatten) is in the protocol JSON; cdp.mjs uses `Target.setAutoAttach` instead.

## 2. Message shape

- Request: `{"id": 7, "method": "Page.navigate", "params": {"url": "..."}, "sessionId": "..."}`.
  `id` is a number you choose and never reuse; `sessionId` is left out for browser-level calls.
- Response: same `id`, with either `"result": {...}` or `"error": {"code": -32000, "message": "..."}`.
  Observed error: code -32000 "Cannot find default execution context" (evaluating in a popup that had no page yet).
- Event: no `id`, has `method`, `params`, and `sessionId` when it belongs to a page, for example
  `{"method":"Page.loadEventFired","params":{"timestamp":1234.5},"sessionId":"..."}`.
- Flat sessions: with `flatten: true` every page gets a `sessionId` and you send all page commands on the one
  WebSocket with that `sessionId` added to the message.

## 3. The calls cdp.mjs makes

| Method or event | Parameters used | What comes back / why |
|---|---|---|
| `Browser.getVersion` | none | `product`, `userAgent` |
| `SystemInfo.getProcessInfo` | none | `processInfo[]` with `type` and `id`; the entry with type `browser` is the real pid |
| `Target.setAutoAttach` | `autoAttach`, `waitForDebuggerOnStart`, `flatten`, `filter` (experimental) | browser level with filter page only; page level for frames and workers |
| `Target.createTarget` | `url` | `targetId` of a new tab |
| event `Target.attachedToTarget` | `sessionId`, `targetInfo`, `waitingForDebugger` | a paused target is waiting for us |
| event `Target.detachedFromTarget` | `sessionId` | forget the session |
| `Runtime.runIfWaitingForDebugger` | none | lets the paused target start (after the guard is on) |
| `Target.closeTarget` | `targetId` | close one tab |
| `Page.enable` | none | needed for page events |
| `Page.navigate` | `url` | `errorText` is set when the navigation failed |
| event `Page.loadEventFired` | none | the page finished loading; wait for it with a timeout |
| `Runtime.evaluate` | `expression`, `returnByValue: true`, `awaitPromise: true` | `result.value`, or `exceptionDetails` |
| `Input.dispatchMouseEvent` | `type` mouseMoved, mousePressed, mouseReleased; `x`, `y`, `button`, `buttons`, `clickCount` | real click, page sees isTrusted true |
| `Input.dispatchKeyEvent` | `type` keyDown, keyUp, rawKeyDown, char; `modifiers` (Alt 1, Ctrl 2, Meta 4, Shift 8); `key`, `code`, `windowsVirtualKeyCode`, `nativeVirtualKeyCode`, `text`, `unmodifiedText` | real key press |
| `Input.insertText` | `text` | experimental; only an input event, no key events |
| `Page.captureScreenshot` | `format` png | `data` is base64 |
| `Fetch.enable` | `patterns: [{urlPattern: '*'}]` | every request now pauses until we answer |
| event `Fetch.requestPaused` | `requestId`, `request.url`, `request.method`, `resourceType`, `redirectedRequestId` | a redirect hop pauses again with `redirectedRequestId` set |
| `Fetch.continueRequest` | `requestId` | let a loopback request go |
| `Fetch.failRequest` | `requestId`, `errorReason: 'BlockedByClient'` | refuse; the value is in Network.ErrorReason |
| `Runtime.enable`, events `Runtime.consoleAPICalled`, `Runtime.exceptionThrown` | none | only with the `console` option |
| `Browser.close` | none | the browser shuts down and drops the WebSocket |

## 4. Order that works

1. Browser level: `Target.setAutoAttach` (autoAttach, waitForDebuggerOnStart, flatten, filter page only).
2. `Target.createTarget`, then wait for `Target.attachedToTarget` for that targetId.
3. On the new session: `Fetch.enable`, `Target.setAutoAttach` (children), `Page.enable`, then
   `Runtime.runIfWaitingForDebugger`. Only now may the page run.
4. Subscribe to `Page.loadEventFired` BEFORE `Page.navigate`, or a fast page is missed.
5. Close with `Browser.close`, wait for the process to exit, delete the temp profile.

## 5. Traps seen on this PC (2026-10-03)

- Edge on Windows: the process node spawns exits with code 0 after 0.07 to 0.4 s while the real browser keeps
  running as another pid. `SystemInfo.getProcessInfo` gives the real pid. Chrome: the spawned process is the browser.
- `Fetch` does not see WebSocket handshakes (the blocked count did not change for a page WebSocket to a foreign host).
  The proxy flag in SKILL.md is what stops them.
- `Runtime.evaluate` works without `Runtime.enable`; enabling it is only needed for console events.
- Do not assume the order of the `Target.createTarget` reply and the `Target.attachedToTarget` event: wait by targetId.
