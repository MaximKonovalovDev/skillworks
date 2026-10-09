# Netcode patterns

Own-word notes for GameNetworkingSockets send flags, connection states and P2P terms, plus smooth-play ideas. Short tokens only; no text copied.

## Connection states

| State | Meaning |
|---|---|
| None | No link yet; the slot is empty. |
| Connecting | Trying to reach the peer now. |
| FindingRoute | Looking for a path to the peer. |
| Connected | Link is live; game traffic may flow. |
| ClosedByMe | I closed the link on purpose. |
| ClosedByPeer | The peer closed the link. |
| FinWait | Told the peer we are done; waiting for its ack. |
| Linger | Link is done but kept a short while to flush. |
| ProblemDetectedLocally | Something looks wrong here; check the link. |

Only Connected carries game traffic. Never send before Connected.

## Send flags

| Flag | Bits | When to use |
|---|---|---|
| Unreliable | 0 | Repeat sends where a loss is fine, like positions. |
| NoNagle | 1 | Send at once; skip the short wait that groups small sends. |
| UnreliableNoNagle | 1 | Repeat sends that must go at once, like urgent positions. |
| NoDelay | 4 | Send at once with no wait on this message. |
| Reliable | 8 | Must arrive; resends until the peer acks, like scores. |
| ReliableNoNagle | 9 | Must arrive and must go at once, like urgent scores. |
| UseCurrentThread | 16 | Off; keep callbacks on the poll thread. |
| AutoRestartBrokenSession | 32 | Off; do not restart a broken session by itself. |

Flag choice: reliable false and urgent false gives Unreliable; false and true gives UnreliableNoNagle; true and false gives Reliable; true and true gives ReliableNoNagle. NoDelay sends at once with no wait. NoNagle skips wait. Reliable resends until acked.

## P2P glossary

| Word | Meaning |
|---|---|
| identity | Who you are on the net; your long-term name. |
| listen socket | A socket that takes new incoming links. |
| connection | One link to one peer. |
| poll group | A set of links read together at once. |
| signaling | Swapping addresses so two peers can meet. |
| NAT traversal | Punching a direct path through home routers. |
| relay | A helper that carries packets when direct fails. |

## Smooth play ideas

- prediction: guess your next move at once so input feels instant.
- reconciliation: fix a wrong guess when the server truth lands.
- interpolation: show others a little in the past to keep motion smooth.
- lag compensation: rewind the world to check a late shot fairly.

Send repeated positions over Unreliable. Send scores and chat over Reliable.

## Size and rate guards

- A message over 1200 bytes may fragment; split it or warn.
- A reliable message over 20 per sec is a warn; the resend cost grows fast.
- Plan caps: size 1 to 524288, per_second over 0 and at most 120.
