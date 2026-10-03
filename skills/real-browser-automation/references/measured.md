# Measured on this PC (2026-10-03)

Everything here was produced by running `scripts/cdp.mjs` against a local page on 127.0.0.1. Windows 10, Node 24.14.
Edge `154.0.4258.53` (`Edg/154.0.4258.53`) and Chrome `154.0.8037.95`. Flags were the script defaults:
`--headless=new --remote-debugging-port=0 --user-data-dir=<temp> --no-first-run --no-default-browser-check
--window-size=1280,800` plus the proxy flags. Anything not listed is "not measured". Values from a different
browser version or PC can differ: measure again before relying on them.

## What the page sees

| Value | Edge 154.0.4258.53 | Chrome 154.0.8037.95 |
|---|---|---|
| `navigator.webdriver` | true | true |
| same, with `--disable-blink-features=AutomationControlled` added | false | false |
| `Object.getOwnPropertyDescriptor(navigator, 'webdriver')` | undefined (not an own property) | undefined |
| `navigator.userAgent` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/154.0.0.0 Safari/537.36` |
| "HeadlessChrome" in the user agent | yes | yes |
| `Browser.getVersion` userAgent equals the page's | yes | yes |
| `navigator.languages` | `["en-US","en"]` | `["en-US","en"]` |
| `navigator.plugins.length`, `navigator.mimeTypes.length` | 5, 2 | 5, 2 |
| `typeof window.chrome`, its keys | object: loadTimes, csi, app | object: loadTimes, csi, app |
| `screen` width x height (also availWidth x availHeight), colorDepth | 800x600, 24 | 800x600, 24 |
| `innerWidth x innerHeight`, `outerWidth x outerHeight` with `--window-size=1280,800` | 1256x708, 1280x800 | 1264x705, 1280x800 |
| same without `--window-size` | 756x488, 780x580 | 764x485, 780x580 |
| `devicePixelRatio` | 1 | 1 |
| `Notification.permission` | default | default |
| `navigator.permissions.query({name:'notifications'})` state | prompt | prompt |
| `navigator.hardwareConcurrency`, `deviceMemory` | 12, 16 | 12, 16 |
| `navigator.platform`, `navigator.vendor` | Win32, Google Inc. | Win32, Google Inc. |
| `navigator.userAgentData` brands, mobile, platform | Chromium/154, Microsoft Edge/154, Not A(Brand/99; false; Windows | Chromium/154, Google Chrome/154, Not A(Brand/99; false; Windows |
| `document.visibilityState`, `document.hasFocus()` | visible, true | visible, true |
| WebGL unmasked renderer, default launch | this PC's real NVIDIA GPU through ANGLE/Direct3D11 (full string left out of this public repo) | same |
| WebGL unmasked renderer with `--disable-gpu` | ANGLE ... Microsoft Basic Render Driver | ANGLE ... Microsoft Basic Render Driver |

Read-out: the screen is a fixed 800x600 while the window is bigger (outer 1280x800), and the user agent says
HeadlessChrome. A detector can use both. `navigator.webdriver` is true as soon as `--remote-debugging-port` is used.

## Events produced by the Input domain (both browsers)

A `Input.dispatchMouseEvent` click gave the page: mousemove, pointerdown, mousedown, mouseup, click, all with
`isTrusted` true; the click had `detail` 1, `pointerType` "mouse", `button` 0, clientX/clientY 58/28 and screenX/screenY
80/118 in Edge, 76/125 in Chrome. `Input.dispatchKeyEvent` typing "aB" gave keydown (key a, code KeyA, keyCode 65,
isTrusted true), input (inputType insertText, isTrusted true), keydown (key B, code KeyB, keyCode 66), input; the same in both
browsers. Typing `Ab-c@1` gave keydown and keyup pairs with codes KeyA, KeyB, Minus, KeyC, Digit2, Digit1 and shiftKey
true for A and @. The mouse moves in one jump to the element centre, so a detector that wants a curved path sees none.

## headless=new versus old

Alone on the command line, `--headless=old`, `--headless` and `--headless=new` each started a working headless
browser in both Edge 154 and Chrome 154, and each reported a user agent containing HeadlessChrome. With
`--headless=old` placed after `--headless=new` in the script's flags, every value in the table above was identical.
I found no difference. Whether the browser maps `old` to the new mode: not verified.

## Does the loopback guard hold? (both browsers)

- `page.goto('http://example.com/')`: throws LocalOnlyError before any request.
- Page `fetch('http://blocked.invalid/x')`: rejected; `browser.blocked` had 1 entry (resourceType XHR).
- A Worker made from a Blob that fetched a foreign URL: rejected, listed in `browser.blocked`.
- An iframe (data: URL) that fetched a foreign URL: rejected, listed.
- A 302 from 127.0.0.1 to a foreign URL: the second hop was blocked (`afterRedirect` true); `goto` failed with net::ERR_BLOCKED_BY_CLIENT.
- Real click on a link with target _blank to a foreign URL (Edge): the new tab's request was listed in `browser.blocked`.
- A page WebSocket to a foreign host: it errored, but the Fetch layer did not list it (blocked count unchanged).
- Fetch layer switched off, proxy layer alone: `fetch` to a foreign host failed with net::ERR_PROXY_CONNECTION_FAILED; a WebSocket to a foreign host errored.
- `http://test.localhost:<port>/` loaded normally with the proxy flags on.
- Not measured: `[::1]` end to end, `https:`, anything on Linux or macOS.

## Speed on this PC (the PC sat at about 90-99 percent CPU from other work, so these are slow-side numbers)

- `launch()`: 1.2 to 3.2 s for both browsers.
- `close()` with the default launch, Edge: 1.2 to 23 s over about 12 runs. Chrome: 0.5 to 36 s over about 28 runs (one run was
  still alive when I stopped timing at 60 s), and about half of them took longer than 10 s.
- `close()` with `--disable-gpu` (Chrome, 4 runs): 0.65 to 3.5 s.
- In one slow Chrome close, 20 s after `Browser.close` the main browser process, the crashpad handler and the GPU process were
  still running while the renderers and utility processes were gone. Likely cause is GPU process teardown; the fast
  `--disable-gpu` runs fit that, but I did not prove it. So: pass `closeTimeout: 60000` to `launch()` (the CLI uses
  60000), or `--disable-gpu` if the WebGL value does not matter. The library default stays 10 s and then throws; it never kills.
- Edge on Windows: the process node spawns exits with code 0 after 0.07 to 0.4 s; the real browser is another pid (`SystemInfo.getProcessInfo`).

## Re-measure

```
node -e "require('http').createServer((q,s)=>s.end('<title>m</title>')).listen(0,'127.0.0.1',function(){console.log(this.address().port);setTimeout(()=>process.exit(0),60000)})"
node scripts/cdp.mjs --url http://127.0.0.1:<port>/ --browser chrome --eval "JSON.stringify([navigator.webdriver, navigator.userAgent, navigator.languages, navigator.plugins.length, typeof window.chrome, [screen.width, screen.height], Notification.permission])"
```

## Not measured

Headed mode, other OS, `Runtime.enable` being visible to a page, how a detector scores these values, Playwright's own
values, behaviour under an enterprise browser policy.
