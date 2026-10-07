# Patterns: symptom to branch

Each recipe starts from a fetch miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## Timeout matched on message text

Symptom: the handler compares the message text to find a timeout and misses.

- Branch on `err.code` after the `isAxiosError` check: `ECONNABORTED` for the aborted connection, `ETIMEDOUT` for the exceeded deadline.
- prints: handler takes the timeout path on `ETIMEDOUT` without reading the message

## Cancelled operation requeued

Symptom: a canceled operation loops back into the queue.

- Check the `__CANCEL__` marker and the `ERR_CANCELED` code with the default `canceled` message first, then stop; the code argument of the `CanceledError` constructor carries `ERR_CANCELED` at line 16.
- prints: canceled operation stops at the line 16 shape, never requeued

## Bad status read off the wrong object

Symptom: a 404 handler reads `response.status` when only the wrapped error survived.

- Branch on `ERR_BAD_RESPONSE` and read `response` plus `status`; `ERR_BAD_REQUEST` marks the malformed request shape instead.
- prints: `ERR_BAD_RESPONSE` handler quotes the server reply and its `status`

## Empty message on dual-stack failure

Symptom: Node throws with a blank message and the log line says nothing.

- Wrap with `AxiosError.from`: it reads the `errors` array of the `AggregateError`, joins each entry `message`, and falls back to `error.name` when the array gives nothing.
- prints: wrapped error carries the joined entry messages

## Secrets in the logged config

Symptom: a logged config leaks a token.

- Set the `redact` array on the config and serialize with `toJSON`; each matching key prints as `REDACTED` at any depth.
- prints: token key prints as `REDACTED`, other keys unchanged

## Logger throws on cause

Symptom: a structured logger throws while serializing the wrapped error.

- Keep `cause` non-enumerable: the wrapped error holds `circular` internals (sockets, requests, agents), so an enumerable link breaks the own-property walk.
- prints: logger walks the error without throwing

## Status lost in wrapping

Symptom: the 404 becomes unreadable after wrapping.

- The constructor takes `status` from `response.status`; `from` copies `error.status` only when the new error has none.
- prints: wrapped error still carries the 404 `status`

## Wrong error kind caught

Symptom: the catch block cannot tell the axios error from the canceled one without instanceof.

- Read `name`: `AxiosError` on the base, `CanceledError` on the subclass; an invalid URL carries `ERR_INVALID_URL`.
- prints: catch quotes `CanceledError` for the canceled operation
