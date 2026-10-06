# Fix patterns per symptom

Each pattern: symptom, the rule, the sanctioned fix, and how to confirm. Run outputs below were measured with gh 2.88.1 on 2026-10-06.

## Wrong host on a repo command

Symptom: a repo command hits `github.com` while the shell sits in a GHES checkout, or `-R other/host/repo` is ignored. Fix: resolve through the command selection path then call `repo.RepoHost()`; never default first. Confirm: the request host equals the selected repo host.

## Explicit flag ignored

Symptom: `--hostname` or a URL flag loses to a configured default. Fix: respect the command existing validation and precedence; never replace it with `DefaultHost()`. Confirm: the explicit host reaches the client unchanged.

## Default treated as selection

Symptom: code branches on `ghinstance.Default()` as if the user chose a host. Fix: treat it as the constant `github.com` and check for an explicit or repository host first. Confirm: `-R` and `GH_REPO` selections survive.

## Gateway bypassed

Symptom: `gh api repos/cli/cli` reaches `api.github.com` although `hosts.yml` sets `api_host: gh-gateway.example.com`. Fix: route through the `go-gh` client with a relative path; never build an absolute `https://api.github.com/...` URL and hand it to an `*http.Client`. Confirm: the request lands on the gateway while login, remotes, and web URLs still show the host.

## Token missing behind a gateway

Symptom: gateway requests arrive without a token. Fix: look up the token via `HostForAPIHost` in `api/http_client.go` so the host token is sent. Confirm: the gateway request carries the host token; a genuinely logged-in host still resolves to its own token.

## gh api assumed central

Symptom: a reviewer expects `gh api` to honor the shared client. Fix: name it a wart: it carries a second implementation because it takes its path verbatim. Confirm: routing changes touch both the client and the `gh api` path.

## Syntax dispute

Symptom: docs mix parentheses for optionals or quotes for placeholders. Fix: use angled brackets for placeholders, square brackets for optionals, braces for required exclusive choices, ellipsis for repeats. Confirm: `gh pr view <issue-number>`, `gh pr checkout [--web]`, `gh pr {view | create}`, `gh pr close <pr-number>...` all parse as documented.

## hub versus gh debate

Symptom: a user expects `gh` to proxy `git` like `hub`. Fix: route git-shaped work to `hub` as a proxy to git and GitHub workflows to `gh` as a standalone opinionated tool. Confirm: the choice matches the book rule.

## Stale agent skill

Symptom: an agent drives `gh` with last-release syntax. Fix: run `gh skill install cli/cli gh --scope user` once and `gh skill update gh` after each release. Confirm: the skill reports the installed release.

## Pin or licence doubt

Symptom: a reviewer doubts the source. Fix: replay the three pinned calls: licence endpoint shows `MIT` and `trunk`; commits/trunk shows `17142e08db2e300b37e6da1ddcfb651eb6d9c587` and `2026-10-05`; contents for `docs/source.md` at the pin shows blob `4f9506774b839969f4b790e841d3daf5d6d642cd` size 1709 with local sha256 prefix `ac46c3d230cf`; `gh --version` shows `2.88.1`. Confirm: all four outputs match on this PC.
