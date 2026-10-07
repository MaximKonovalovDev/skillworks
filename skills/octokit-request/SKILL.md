---
name: octokit-request
description: Use when handling an octokit fetch failure: abort versus network TypeError, empty versus error statuses, message building, body parsing, and hook defaults, with the exact branch to take.
version: 0.1.0
author: skillworks
license: MIT
---

# octokit request-wrapper errors

Fix-first rules distilled from octokit/request.js at `999fad9c` (main, pushed 2026-10-05) for the GitHub timeout fetch class: which branch names the failure, which status travels with it, and which replay proves the pin. Each rule names the exact token to branch on. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`.

## Abort versus network error

- Check `error.name` for `AbortError` first (line 58): stamp `status` 500 on the same error and rethrow it, never wrap the abort in a new `RequestError` [src: fetch-wrapper.ts catch]
- Unwrap undici network faults on `TypeError` via `cause`: an `Error` cause gives `cause.message`, a string `cause` passes through, otherwise keep `error.message`, then throw `RequestError` with `500` [src: fetch-wrapper.ts catch]

## Empty and conditional statuses

- Return the empty response at once for `204` or `205`; for a `HEAD` request return it when `status` is under 400 and throw `RequestError` with `statusText` at 400 or more [src: fetch-wrapper.ts HEAD]
- On `304` read the body first with `getResponseData`, then throw `RequestError` carrying `Not modified` with the 304 `status` [src: fetch-wrapper.ts 304]

## Error messages and bodies

- Build failure text with `toErrorMessage`: a string body passes through, an `arrayBuffer` body yields `Unknown error`, and an object `message` gains a `documentation_url` suffix with joined `errors` entries [src: fetch-wrapper.ts toErrorMessage]
- Parse bodies on the `content-type` header: `application/json` plus scim+json is text-read then parsed, text or utf-8 charset (never octet-stream) returns text, anything else returns `arrayBuffer` [src: fetch-wrapper.ts getResponseData]

## Defaults and request options

- Route through `endpoint.parse`: call `fetchWrapper` directly when `endpointOptions.request` has no `hook`, otherwise hand the inner closure (carrying `endpoint` and `defaults`) to the `hook` [src: with-defaults.ts]
- Forward abort and streams with `signal` plus `duplex` half when a body exists, and warn on the `deprecation` link header with its `sunset` date while coercing headers to string [src: fetch-wrapper.ts options]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n "AbortError" work/octokit-request/src/fetch-wrapper.ts
```

prints 2 match lines: the comment at line 52 and the check `58:      if (error.name === "AbortError") {` - the branch stamps `status` 500 on the abort. `rg -n "status >= 400" work/octokit-request/src/fetch-wrapper.ts` prints line `140:  if (status >= 400) {`, whose branch throws `RequestError` via `toErrorMessage`. `rg -n "toErrorMessage" work/octokit-request/src/fetch-wrapper.ts` prints lines 143 and `197:function toErrorMessage(data: unknown) {`, the helper that appends `documentation_url`. `rg -l "fetchWrapper" work/octokit-request/src/` lists 2 files: `work/octokit-request/src/fetch-wrapper.ts` and `work/octokit-request/src/with-defaults.ts`.
