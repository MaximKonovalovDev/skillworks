# Playwright notes: what carries over, and step 2

Source: microsoft/playwright docs (`docs/src/*.md`, Apache-2.0) read at tag v1.63.0, commit
`1b025d7e20a026371cd5f98ba0cdce48892737c8`, verified 2026-10-03. Only ideas are used here, no text and no code
copied. Files consulted: actionability, locators, browser-contexts, network, browsers, library-js, input,
screenshots, evaluating, navigations, pages, and the API files class-page, class-browsercontext,
class-browsertype, class-route, class-locator, class-browser, params.

## What carries over into scripts/cdp.mjs

1. Auto-waiting. Playwright checks, before a click, that the locator resolves to one element and that the
   element is visible, stable (same box for two animation frames), receives events (nothing covers the click
   point) and is enabled. `Locator.fill` also needs the element editable. cdp.mjs `click()` does the same four
   checks by polling inside the page (box not empty, not hidden, not disabled, `elementFromPoint` is the
   element, same position on two polls) and names the failed check in its timeout error. Never use a fixed sleep.
2. Locators first. Playwright recommends user-facing locators (`getByRole`, `getByText`, `getByLabel`,
   `getByPlaceholder`, `getByTestId`) over long CSS or XPath. cdp.mjs takes only CSS selectors, so on a site we
   own, put a stable `data-testid` on every control and select with `[data-testid="login-submit"]`.
3. Isolation with browser contexts. A Playwright `BrowserContext` is a clean incognito-like profile with its own
   storage and cookies; each test gets a new one. cdp.mjs gets the same result the simple way: one fresh temporary
   `--user-data-dir` per `launch()`, deleted after `close()`. The protocol also has `Target.createBrowserContext`
   (parameters disposeOnDetach, proxyServer, proxyBypassList, originsWithUniversalNetworkAccess); cdp.mjs does not use it.
4. Request routing and blocking. `page.route(url, handler)` and `context.route(url, handler)` hold every matching
   request until the handler calls `route.abort()`, `route.continue()` or `route.fulfill()`. The JS `url`
   argument may be a glob, a RegExp, a URLPattern or a function that gets a URL. cdp.mjs does the same with
   `Fetch.enable` plus `Fetch.requestPaused` and `Fetch.failRequest`. Two traps from the Playwright docs also hold for raw CDP:
   a Service Worker can answer requests without routing seeing them (Playwright advises `serviceWorkers: 'block'`
   on the context), and `page.route` misses the first request of a popup (use `context.route`). cdp.mjs attaches
   to popups paused at start, and also sends all non-loopback traffic to a dead local proxy as a second layer.
5. Installed browsers. Playwright can drive branded Chrome and Edge already on the machine: option `channel`
   with `chrome`, `msedge`, `chrome-beta`, `msedge-beta`, `chrome-dev`, `msedge-dev`, `chrome-canary`,
   `msedge-canary`. It does not install them by default. `channel: 'chromium'` opts in to the new headless mode.
   The docs warn that Chrome and Edge use the new headless implementation, which differs from Playwright's
   default chromium headless shell, and that enterprise browser policies can stop Playwright from launching them.
6. Library vs test runner. The docs say that for end-to-end testing you normally want `@playwright/test`, and
   that the `playwright` package is the library for driving a browser directly from your own script.

## Step 2: when the project adds the `playwright` devDependency

Do this only when the project (not this skill) has added `playwright` to `package.json` devDependencies.
Reasons to move: you need locators and auto-waiting everywhere, or many pages and contexts at once.
Keep the same loopback rule.

```js
import { chromium } from 'playwright';

const local = u => ['127.0.0.1', 'localhost', '[::1]'].includes(u.hostname) || u.hostname.endsWith('.localhost');

const browser = await chromium.launch({ channel: 'msedge' });            // the installed Edge, headless by default
const context = await browser.newContext({ serviceWorkers: 'block' });   // routing cannot see service workers
await context.route(u => !local(u), route => route.abort());             // nothing leaves the machine
const page = await context.newPage();
await page.goto('http://127.0.0.1:8080/');
await page.getByLabel('Name').pressSequentially('Ada');                  // keydown, keypress/input, keyup per character
await page.getByRole('button', { name: 'Go' }).click();                  // auto-waits, then clicks
console.log(await page.evaluate(() => navigator.webdriver));
await page.screenshot({ path: 'out.png' });
await browser.close();
```

Notes on the names used above, all found in the docs read:
- `chromium.launch({ channel })`, `browser.newContext({ serviceWorkers })`, `context.route(url, handler)`,
  `route.abort()`, `context.newPage()`, `page.goto`, `page.evaluate`, `page.screenshot({ path })`, `browser.close()`.
- `Locator.fill` sets the value and triggers one `input` event; `Locator.pressSequentially` sends keydown,
  keypress/input and keyup for each character. For a bot-detection lab where the page watches key events, use
  `pressSequentially` or `press`, not `fill`.
- Custom browser `args` are allowed (Playwright warns they may break it); the loopback proxy flags from cdp.mjs can be passed there.
- Not measured: how `navigator.webdriver` and the other values in measured.md look under Playwright. Measure
  before assuming they match cdp.mjs.
