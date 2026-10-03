# Sources

Licences were verified live on 2026-10-03 with `gh api repos/<owner>/<repo>` (field `license.spdx_id`) and by
reading each repository's LICENSE file. Commit SHAs were read with `gh api repos/<owner>/<repo>/commits/<ref>`.
Ideas and facts were taken. No text was copied from either repository, no code was copied, and cdp.mjs is original.

## 1. microsoft/playwright (docs)

- URL: https://github.com/microsoft/playwright
- Licence: Apache-2.0 (verified 2026-10-03: API says Apache-2.0; LICENSE file is the Apache License 2.0, copyright Microsoft Corporation and Google Inc.)
- Pinned: tag `v1.63.0` (published 2026-09-04), commit `1b025d7e20a026371cd5f98ba0cdce48892737c8`.
  Main branch head seen the same day: `7ad3fba1aad9471c7e46d67a11b0e710a5d77ea8` (not used).
- Read through `gh api repos/microsoft/playwright/contents/docs/src/<file>.md?ref=<sha>` (decoded base64):
  actionability, locators, browser-contexts, network, browsers, library-js, input, screenshots, evaluating,
  navigations, pages, and under `docs/src/api/`: class-page, class-browsercontext, class-browsertype, class-route,
  class-locator, class-browser, params.
- Taken (ideas only): auto-waiting and the actionability checks (visible, stable, receives events, enabled, editable);
  user-facing locators first; browser contexts as clean isolation; request routing with abort/continue/fulfill and its
  service-worker and popup traps; `channel: 'msedge'` / `'chrome'` for installed browsers and the new-headless note;
  library versus test runner; `fill` versus `pressSequentially`. Written in our own words in `references/playwright-notes.md`.

## 2. ChromeDevTools/devtools-protocol (protocol JSON)

- URL: https://github.com/ChromeDevTools/devtools-protocol
- Licence: BSD-3-Clause (verified 2026-10-03: API says BSD-3-Clause; LICENSE file is the three-clause BSD text, copyright The Chromium Authors)
- Pinned: branch master, commit `d209a9a38897d2935a078a0bf00ca821811d21ed` (2026-10-03), protocol version 1.3.
- Files used: `json/browser_protocol.json` and `json/js_protocol.json` (Runtime lives there) at that commit, fetched from
  https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/d209a9a38897d2935a078a0bf00ca821811d21ed/json/browser_protocol.json
- Taken (facts): every method, event and parameter name written in this skill was checked against the JSON; see
  `references/cdp-basics.md`. Descriptions in that file are our own words.

## 3. Our own work

- `scripts/cdp.mjs` and the tests are original, MIT (scaffold). The measured numbers in `references/measured.md` come
  from running that script on this PC; they are not from any source above.
