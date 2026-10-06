# Glossary: the playwright-docs words that decide a test

- strict: a locator that throws instead of picking when more than one element matches.
- actionability: the Visible, Stable, Enabled, Editable, Receives Events checks before any click.
- Hydration: the client pass that makes server-rendered markup interactive; clicks before it miss.
- BFCache: the Back/Forward Cache that restores a page without reloading it; load handlers never fire.
- Waiting for navigation: the `page.waitForURL` pattern that waits for the move the click causes.
- isolated: one BrowserContext per test, so cookies and storage never leak between tests.
- Trace Viewer: the offline `trace.zip` reader with timeline, actions, DOM snapshots, and network.
- Playwright Inspector: the `PWDEBUG=1` stepper that walks a test and picks locators.
- signed in state: the saved `storageState` file shared across tests instead of logging in again.
- Mock APIs: `page.route` interceptions answered with `route.fulfill`, so tests run offline.
- Frame objects: `frameLocator` handles that reach inside iframes without switching context.
- Multiple pages: popups and tabs owned by one BrowserContext, awaited with `waitForEvent('page')`.
- codegen: the recorder that generates user-facing locators from real clicks.
- web first assertions: `expect` checks that retry until the condition holds or times out.
- storageState: the JSON file carrying cookies and local storage from one login to every test.
- main: the default branch the pinned docs were read from; anything else means the pin moved.
- sha: the blob fingerprint the contents endpoint returns; the LICENSE one starts `df112373`.
- sha256: the local download fingerprint; locators.md starts `ca8a0035dc87cf97`.
