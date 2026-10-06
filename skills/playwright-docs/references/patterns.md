# Patterns: symptom to rule for browser rework

## Two buttons match, the click throws

Symptom: `page.getByRole('button').click()` throws naming strict mode.
Do: read the message, add the name or filter so the locator matches one element.
Never: append `first` or `nth` and ship it; the next page change clicks the wrong one.

## The click misses a moving target

Symptom: the click lands on the overlay, or the element detaches mid-click.
Do: let the actionability checks wait; assert visibility first with a web first assertion.
Never: pass `force: true`; it clicks through the symptom and banks the flake.

## Green locally, red after every navigation

Symptom: the test passes alone and flakes in the suite around a link or a back button.
Do: name Hydration or BFCache, then wait for the navigation with `page.waitForURL`.
Never: add a fixed wait and hope; the next slow CI run breaks it again.

## CI-only failure with no local repro

Symptom: the suite fails on the runner and passes on the laptop.
Do: open the Trace Viewer trace, then step the Playwright Inspector; turn on `DEBUG=pw:api` last.
Never: debug by adding logging and rerunning; the trace already recorded everything.

## The suite spends half its time logging in

Symptom: every test fills the login form before doing anything.
Do: sign in once in setup, save `storageState`, and load it in every project.
Never: commit passwords to the repo to make login faster; the state file replaces the login, not the secret.

## The test needs a backend that is down

Symptom: the test hits staging and flakes with the network.
Do: serve Mock APIs with `page.route` and `route.fulfill`; reach frames with `frameLocator`; await popups with `waitForEvent('page')`.
Never: point the test at production to make it pass; the mock is the backend now.

## The docs answer looks wrong

Symptom: a rule above disagrees with the pinned docs.
Do: recheck the licence (`Apache-2.0`, branch `main`), the LICENSE blob sha (`df112373`), and the file hash (`ca8a0035dc87cf97`); a mismatch means the source moved, not that the rule is wrong.
Never: read a guessed docs path and trust a 404 body; misses belong to the read-miss class.
