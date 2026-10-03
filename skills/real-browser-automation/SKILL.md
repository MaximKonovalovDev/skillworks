---
name: real-browser-automation
description: Drives the installed headless Edge or Chrome from Node 24 over the Chrome DevTools protocol (CDP) with only the built-in WebSocket and fetch, against 127.0.0.1 only. Use when a bot, test or journey must be a real browser (real clicks and keys, navigator.webdriver, a beacon the browser itself sends) and before adding Playwright.
license: Apache-2.0 (Playwright notes), BSD-3-Clause (protocol), MIT (scaffold)
---

# real-browser-automation

Run the INSTALLED Edge (first) or Chrome, headless, from Node 24, no npm package. Our own local site only:
127.0.0.1, localhost, [::1], *.localhost. Run from this skill's folder, or give the full path to `scripts/cdp.mjs`.

## Do this first

```
node scripts/cdp.mjs --url http://127.0.0.1:8080/ --eval "navigator.webdriver" --screenshot out.png
```

Steps run in the order given: `--wait-for CSS`, `--click CSS`, `--type "CSS=text"`, `--press Enter`, `--eval JS`.
It prints one JSON object (`eval` results, `blockedRequests`, `closed`). Exit 0 ok, 1 error, 3 refused (host not loopback).
`--check-url URL` prints ALLOW or REFUSE and starts no browser. `--browser chrome` picks Chrome.

From code:

```js
import { launch } from './scripts/cdp.mjs';
const browser = await launch({ closeTimeout: 60000 });    // Edge first, then Chrome; fresh temp profile
try {
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8080/');               // waits for the load event; non-loopback throws
  console.log(await page.evaluate('navigator.webdriver')); // value back, promises awaited
  await page.type('#name', 'Ada');                         // real click to focus, then real key events
  await page.click('#go');                                 // waits: visible, still, not covered
  await page.screenshot('out.png');
  console.log(browser.blocked);                            // requests the guard refused; [] is good
} finally {
  await browser.close();                                   // Browser.close, wait for exit, drop the profile
}
```

Also: `page.press('Enter')`, `page.waitForActionable(css)`, `page.evaluate(fn, ...args)`, `launch({ browser: 'chrome', console: true })`.

## The steps in CDP words

1. Start: `--headless=new --remote-debugging-port=0 --user-data-dir=<fresh temp dir> --no-first-run --no-default-browser-check`. Port 0 means the browser picks a free port.
2. Find the port: read the file `DevToolsActivePort` in the profile dir. Line 1 is the port, line 2 the browser WebSocket path. Retry the read: it can be locked while written.
3. Connect: `new WebSocket('ws://127.0.0.1:<port><path>')`, global in Node 24. Messages are JSON: `{id, method, params, sessionId}`. A reply has the same `id` with `result` or `error`. An event has no `id`.
4. Page: `Target.createTarget`, attach with flat sessions (`Target.setAutoAttach`, flatten true). Navigate with `Page.navigate`, then wait for the event `Page.loadEventFired`, with a timeout.
5. Evaluate: `Runtime.evaluate` with `returnByValue` and `awaitPromise`.
6. Click: `Input.dispatchMouseEvent` mouseMoved, mousePressed, mouseReleased at the element centre. Type: `Input.dispatchKeyEvent` keyDown (with `text`) and keyUp per key. The page sees `isTrusted` true.
7. Screenshot: `Page.captureScreenshot`, base64 PNG.
8. Close: `Browser.close`, then wait for the process to exit.

The raw version with no library, and every method checked against the protocol file: `references/cdp-basics.md`.

## Loopback only, three layers

1. `assertLocal(url)` runs on every `goto`: only http, https, ws, wss on 127.0.0.1, localhost, [::1], *.localhost. data:, file:, about:, chrome: and the rest throw `LocalOnlyError` unless you pass `allow: ['data:']`.
2. `Fetch.enable` on every page, popup, frame and worker pauses each request the page makes. A foreign URL is failed (`BlockedByClient`) and added to `browser.blocked`, redirect hops too.
3. Browser flags `--proxy-server=http://127.0.0.1:9` plus a bypass list for loopback: everything else goes to a dead local port and fails. This also stops WebSockets, which Fetch cannot see.

For many browsers at once, test the guard: `--check-url` for a list of hosts, and one page that fetches a foreign URL, expecting `browser.blocked.length` 1.

## Measured here (Edge 154, Chrome 154, 2026-10-03; table in `references/measured.md`)

- `navigator.webdriver` is true under `--remote-debugging-port`; false after adding `--disable-blink-features=AutomationControlled`.
- `navigator.userAgent` contains HeadlessChrome. `screen` is 800x600 even with a 1280x800 window. plugins 5, languages en-US and en, `window.chrome` exists, `Notification.permission` default.
- Click and key events reach the page with `isTrusted` true. The mouse jumps to the target in one move.

## Gotchas

- Slow close: with the real GPU, `Browser.close` took 0.5 to 36 s on this busy PC. Default wait is 10 s, then it throws and does NOT kill; pass `closeTimeout: 60000`. `--disable-gpu` closed in under 4 s but changes WebGL values.
- Edge on Windows: the process node starts exits at once; the script gets the real pid from `SystemInfo.getProcessInfo`.
- Wait for the element, never sleep a fixed time. Selectors are CSS only; no shadow DOM, no iframe content.
- `evaluate` returns JSON values; a DOM node comes back empty. Characters with no US key (Hebrew, emoji) are inserted as text with no key events.
- After a crash, a `cdp-profile-*` folder may stay in the temp dir. Delete it only when no browser uses it.

## Never

- Any host that is not 127.0.0.1, localhost, [::1] or *.localhost. `allow` never admits a host (http and https entries are ignored); use it for a test page only.
- `--remote-debugging-address`, `--remote-allow-origins=*`, or any port open to the network.
- Kill a process: no taskkill, Stop-Process, process.kill, kill -9. `Browser.close` shuts the whole browser down; in the runs I followed to the end the process ended on its own, even the slow ones. If it times out, wait and look.
- The user's real browser profile, logins or cookies. Fresh temp profile only.
- Turn off `fetchGuard` or `proxyGuard` (they exist so a test can prove each layer alone).
- Run without `try` / `finally` around `browser.close()`.

## Step 2: Playwright

Only when the project itself adds `playwright` as a devDependency: `chromium.launch({ channel: 'msedge' })` uses the
installed Edge. Same rules apply. Recipe and what carries over: `references/playwright-notes.md`.
Sources and licences: `references/sources.md`.
