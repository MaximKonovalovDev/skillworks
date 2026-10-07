# Cheatsheet: axios fetch-error codes

One page. Every line replayed or listed from the axios sources at `2b169bbb`.

## Codes

| See | Branch |
|---|---|
| aborted connection | `ECONNABORTED` on `err.code` |
| exceeded deadline | `ETIMEDOUT` on `err.code` |
| proves axios origin | `isAxiosError` true |
| canceled operation | `ERR_CANCELED`, message `canceled`, marker `__CANCEL__` |
| bad status | `ERR_BAD_RESPONSE`, reply on `response`, `status` on the error |
| malformed request | `ERR_BAD_REQUEST` |
| invalid URL | `ERR_INVALID_URL` |

## Wrapping

| Want | Type |
|---|---|
| usable message from blank throw | `AxiosError.from`, reads `errors`, joins `message` |
| fallback when the array gives nothing | `error.name` |
| keep loggers safe | `cause` non-enumerable (`circular` internals) |
| keep 404 readable | `status` from `response.status`, `from` copies `error.status` |
| tell kinds apart | `name`: `AxiosError` vs `CanceledError` |

## Safe logging

| Want | Type |
|---|---|
| hide sensitive keys | `redact` array on the config |
| placeholder | `REDACTED` |
| serializer | `toJSON` |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "ERR_CANCELED" work/axios-get/src/CanceledError.js` | line 16, code argument `ERR_CANCELED` |
| `rg -n "ECONNABORTED" work/axios-get/src/AxiosError.js` | 2 match lines, static at line 206 |
| `rg -n "isAxiosError" work/axios-get/src/AxiosError.js` | line 161, `this.isAxiosError = true;` |
| `rg -l "CanceledError" work/axios-get/src/` | 1 file: `work/axios-get/src/CanceledError.js` |
