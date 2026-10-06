# Cheatsheet: playwright-docs on one page

- One element or throw: `page.getByRole('button')` is strict; `count()` takes many.
- Narrow, never index: `filter({ hasText: 'Product 2' })`, user-facing locators first.
- Clicks wait: Visible, Stable, Enabled, Editable, Receives Events; no `force: true`.
- Navigations: Hydration plus BFCache explain flakes; `page.waitForURL('**/done')` fixes them.
- Philosophy: Test user-visible behavior; isolated contexts; no third-party tests.
- Practice: locators, chaining, `codegen`, web first assertions.
- Debug order: Trace Viewer trace, Playwright Inspector (`PWDEBUG=1`), `DEBUG=pw:api` last.
- Auth: sign in once, `storageState: 'state.json'`, share everywhere.
- Offline: `page.route('**/api/**', route => route.fulfill({ json: [] }))`.
- Frames and popups: `frameLocator('#frame')`, `context.waitForEvent('page')`.
- Pin: d0fd0f22 on main, Apache-2.0, LICENSE `df112373`, locators.md 47224 bytes `ca8a0035dc87cf97`.
