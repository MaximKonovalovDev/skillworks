# Patterns: symptom to branch

Each recipe starts from a fetch miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## Aborted fetch wrapped and lost

Symptom: an aborted fetch is wrapped in a fresh error and the caller cannot tell it was an abort.

- Check `error.name` for `AbortError` at line 58 first: stamp `status` 500 on the same error and rethrow it, never a new `RequestError`.
- prints: abort keeps its name with the 500 status on the original object

## Network failure message says TypeError

Symptom: the log line says only TypeError and the real network reason is hidden in the wrapper.

- Unwrap `cause` on a `TypeError`: an `Error` cause gives `cause.message`, a string `cause` passes through, otherwise keep `error.message`; then throw `RequestError` with `500`.
- prints: wrapped error carries the undici cause text with status 500

## Empty status parsed as data

Symptom: a 204 or a successful HEAD is fed to the body parser and throws.

- Return the empty response at once for `204` or `205`; for a `HEAD` request return it when `status` is under 400 and throw `RequestError` with `statusText` at 400 or more.
- prints: `204` handler returns before any parse, failed `HEAD` quotes its status

## Conditional request loses its body

Symptom: a 304 handler throws without reading the cached payload first.

- On `304` read the body first with `getResponseData`, then throw `RequestError` carrying `Not modified` with the 304 `status`.
- prints: `Not modified` error still carries the parsed data

## Bare status with no message

Symptom: a 400-plus reply throws with an empty or unreadable message.

- Build the text with `toErrorMessage`: a string body passes through, an `arrayBuffer` body yields `Unknown error`, and an object `message` gains a `documentation_url` suffix with joined `errors` entries.
- prints: 404 handler quotes the message plus its docs link

## Wrong body reader for the type

Symptom: a binary body is decoded as text, or JSON text is returned raw.

- Branch on the `content-type` header: `application/json` plus scim+json is text-read then parsed with a text fallback; text or utf-8 charset (never octet-stream) returns text; anything else returns `arrayBuffer`.
- prints: JSON body parses, binary body arrives as a buffer

## Hook bypassed or defaults dropped

Symptom: a custom hook never runs, or endpoint defaults vanish on the retry path.

- Route through `endpoint.parse`: call `fetchWrapper` directly when `endpointOptions.request` has no `hook`, otherwise hand the inner closure (carrying `endpoint` and `defaults`) to the `hook`.
- prints: hooked call reaches the hook, direct call keeps its defaults

## Abort signal or stream option missing

Symptom: cancellation never reaches the fetch, or a streamed upload fails without its option.

- Forward the abort via `signal` from the request options, set `duplex` half only when a body is present, and warn on the `deprecation` link header with its `sunset` date.
- prints: aborted call stops at the signal, streamed call carries duplex half
