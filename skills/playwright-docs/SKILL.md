---
name: playwright-docs
description: Use when writing Playwright browser tests that flake on locators, waiting, or isolation: strict locators, actionability checks, navigation waiting, trace debugging, auth reuse, and network mocking with the exact call to type.
version: 0.1.0
author: skillworks
license: MIT
---

# Playwright docs distilled

Fix-first rules distilled from the microsoft/playwright docs (d0fd0f22) for the browser rework class: which locator wins, which readiness checks gate a click, which wait survives hydration and cache restores, which two debuggers open first, how one login serves every test, and how a fake backend replaces the network. Each rule names the exact call to type and the output fragment that proves it. Detail lives in `references/cheatsheet.md`, `references/glossary.md`, and `references/patterns.md`. The runnable proof of every rule is `references/pairs.md` (machine list `references/pairs.json`), replayed by `scripts/playwright_docs.py`.

## Locators are strict

- Click with `page.getByRole('button')`: strict mode throws when the locator matches more than one element, so a locator guarantees exactly one element and `count()` is the only call that accepts many [src: references/pairs.md#pw-p04]
- Prefer user-facing locators `getByRole`, `getByLabel`, `getByPlaceholder`, and `getByText` over CSS or XPath, and narrow a list with `filter({ hasText: 'Product 2' })` instead of indexing into it [src: references/pairs.md#pw-p04]
- Never silence strictness with `first`, `last`, or `nth` to pick a winner: when the page changes the click lands where it was never meant to, so write a locator that matches one element [src: references/pairs.md#pw-p04]

## Actionability gates every click

- Before Playwright clicks it runs the Visible, Stable, Enabled, Editable, and Receives Events checks, so a covered or animating target waits instead of missing [src: references/pairs.md#pw-p05]
- Never pass `force: true` to skip the checks: forcing clicks hidden or detached elements directly and the docs discourage it because the pass hides the real breakage [src: references/pairs.md#pw-p05]

## Navigations wait, they never hope

- Name the two flake makers Hydration and BFCache: hydration makes the first render interactive late, and the Back/Forward Cache restores pages without reloading them [src: references/pairs.md#pw-p06]
- Wait with the Waiting for navigation pattern `page.waitForURL('**/done')` after the click that moves, never a fixed sleep then hope [src: references/pairs.md#pw-p06]

## Test what the user sees

- Hold the Testing philosophy line Test user-visible behavior, keep tests isolated with their own BrowserContexts, and never test third-party dependencies [src: references/pairs.md#pw-p07]
- Follow the Best Practices list: use locators with chaining and filtering, generate them with `codegen`, and assert with web first assertions that retry until the condition holds [src: references/pairs.md#pw-p07]

## Debug with the trace first

- Open the Trace Viewer trace first: one `trace.zip` shows the timeline, every action, the DOM snapshot at each step, and the network log, which a rerun cannot reproduce [src: references/pairs.md#pw-p08]
- Step the Playwright Inspector next with `PWDEBUG=1`: it walks the test line by line and picks the locator for you, and verbose `DEBUG=pw:api` logs earn their keep only when the trace still does not explain the failure [src: references/pairs.md#pw-p08]

## Log in once, reuse everywhere

- Follow the Core concepts reuse pattern: sign in once, save the signed in state with `storageState: 'state.json'`, and share that file across tests and projects instead of logging in per test [src: references/pairs.md#pw-p09]

## Fake the backend, frame the page

- Serve Mock APIs with `page.route('**/api/**', route => route.fulfill({ json: [] }))`: the test runs offline against the fake and never hits the production API [src: references/pairs.md#pw-p10]
- Reach inside an iframe through Frame objects with `page.frameLocator('#frame').getByRole('button')`, and catch a popup through Multiple pages with `context.waitForEvent('page')`, because one test routinely drives more than one page [src: references/pairs.md#pw-p11]

## Provenance of every line above

- The licence is Apache-2.0 on the main branch: the repos endpoint answers `{"license": "Apache-2.0", "branch": "main"}` and anything else means the pin moved [src: references/pairs.md#pw-p01]
- The LICENSE blob sha starts with `df112373`: read it through the contents endpoint at the pinned ref and treat any other sha as a different book [src: references/pairs.md#pw-p02]
- A guessed path answers Not Found with exit 1 and a `documentation_url` pointing at the get-repository-content endpoint: that miss belongs to the read-miss class, never to a passing read [src: references/pairs.md#pw-p03]
- The locators.md download is 47224 bytes and its sha256 starts with `ca8a0035dc87cf97`: hash the file in `work/playwright-docs/src/` and treat a mismatch as a corrupt source [src: references/pairs.md#pw-p12]

## Fix-first workflow

Run the failing test and read the symptom: two matching buttons need the strictness rule, a click that misses needs the actionability rule, a flake after navigation needs the waiting rule, a CI-only failure needs the trace rule, a slow suite needs the auth rule, a backend dependency needs the mock rule. The per-symptom recipes are in `references/patterns.md` and the one-page reminder in `references/cheatsheet.md`.
