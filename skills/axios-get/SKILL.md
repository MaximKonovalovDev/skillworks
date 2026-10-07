---
name: axios-get
description: Use when handling an axios fetch failure: timeout versus abort codes, cancel markers, bad-response versus bad-request codes, AggregateError wrapping, redacted logging, cause handling, and status travel, with the exact codes to branch on.
version: 0.1.0
author: skillworks
license: MIT
---

# axios fetch-error codes

Fix-first rules distilled from axios/axios at `2b169bbb` (v1.x, pushed 2026-10-06) for the fetch-failure class: which code names the failure, which flag proves the error came from axios, and which replay proves the pin. Each rule names the exact token to branch on. Detail lives in `references/patterns.md`, terms in `references/glossary.md`, the one-page reminder in `references/cheatsheet.md`.

## Timeout versus abort

- Branch a timeout on `err.code`, never on the message text: `ECONNABORTED` names the aborted connection and `ETIMEDOUT` names the exceeded deadline; confirm the error came from axios with `isAxiosError` first [src: AxiosError.js statics]
- Treat a cancellation as its own kind: `CanceledError` passes `ERR_CANCELED` as the code argument, defaults the message to `canceled`, and sets the `__CANCEL__` marker to true; never turn it into a retry loop [src: CanceledError.js constructor]

## Bad response versus bad request

- Read the server reply off `response` when the code is `ERR_BAD_RESPONSE` (the `status` travels on the error too); use `ERR_BAD_REQUEST` for a malformed request shape where the reply carries less [src: AxiosError.js statics]

## Aggregate and wrapped errors

- Unwrap dual-stack failures with `AxiosError.from`: it reads the `errors` array of an `AggregateError`, joins each entry `message` into one line, and falls back to `error.name` when the array gives nothing [src: AxiosError.js from]
- Keep `cause` non-enumerable: the wrapped error holds `circular` internals (sockets, requests, agents), and an enumerable link makes structured loggers throw while serializing [src: AxiosError.js from]

## Redacted logging

- Log safely with `toJSON`: list sensitive keys in the `redact` array on the config and each matching key prints as `REDACTED` at any depth; without the array the serialization stays unchanged [src: AxiosError.js toJSON]

## Status travel and names

- Take `status` from `response.status` in the constructor; `from` copies `error.status` only when the new error has none, which keeps a fetch 404 readable after wrapping [src: AxiosError.js constructor plus from]
- Tell errors apart without instanceof: the base sets `name` to `AxiosError` and the subclass sets `name` to `CanceledError`; an invalid URL carries `ERR_INVALID_URL` instead [src: CanceledError.js plus AxiosError.js statics]

## Prove the pin

Replayed live 2026-10-07 with the installed `rg` (each replay ends exit 0):

```
rg -n "ERR_CANCELED" work/axios-get/src/CanceledError.js
```

prints 1 match line: `16:    super(message == null ? 'canceled' : message, AxiosError.ERR_CANCELED, config, request);` - the code argument carries `ERR_CANCELED` with the default `canceled` message. `rg -n "ECONNABORTED" work/axios-get/src/AxiosError.js` prints 2 match lines: the doc line 137 and the static at line 206 (`AxiosError.ECONNABORTED = 'ECONNABORTED';`). `rg -n "isAxiosError" work/axios-get/src/AxiosError.js` prints the flag line `161:    this.isAxiosError = true;`, set by the `AxiosError` constructor. `rg -l "CanceledError" work/axios-get/src/` lists 1 file: `work/axios-get/src/CanceledError.js`.
