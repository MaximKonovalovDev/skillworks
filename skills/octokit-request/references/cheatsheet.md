# Cheatsheet: octokit request-wrapper errors

One page. Every line replayed or listed from the octokit sources at `999fad9c`.

## Errors

| See | Branch |
|---|---|
| aborted fetch | `error.name` is `AbortError` at line 58, `status` 500, rethrow as-is |
| network fault | `TypeError` with `cause`: `Error` gives `cause.message`, string passes through |
| wrapper for the rest | `RequestError` with `500` |
| empty success | `204` or `205` returns at once |
| probe request | `HEAD` under 400 returns, at 400 or more throws with `statusText` |
| conditional hit | `304` reads via `getResponseData`, throws `Not modified` |
| failed status | `status >= 400` at line 140 throws `RequestError` |

## Messages and bodies

| Want | Type |
|---|---|
| failure text | `toErrorMessage` defined at line 197, called at line 143 |
| string body | passes through |
| binary body | `arrayBuffer` yields `Unknown error` |
| object body | `message` plus `documentation_url` suffix, joined `errors` |
| JSON body | `content-type` `application/json` plus scim+json, text-read then parse |
| text body | text or utf-8 charset except octet-stream returns text |
| other body | returns `arrayBuffer` |

## Defaults and options

| Want | Type |
|---|---|
| no hook set | `fetchWrapper` on `endpoint.parse` output |
| hook set | inner closure with `endpoint` plus `defaults` goes to the `hook` |
| abort an in-flight call | `signal` option |
| stream a body | `duplex` half when a body exists |
| spot a removal | `deprecation` link header plus `sunset` date |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "AbortError" work/octokit-request/src/fetch-wrapper.ts` | 2 match lines, check at line 58 |
| `rg -n "status >= 400" work/octokit-request/src/fetch-wrapper.ts` | line 140, branch throws `RequestError` |
| `rg -n "toErrorMessage" work/octokit-request/src/fetch-wrapper.ts` | lines 143 and 197, appends `documentation_url` |
| `rg -l "fetchWrapper" work/octokit-request/src/` | 2 files: `fetch-wrapper.ts` plus `with-defaults.ts` |
