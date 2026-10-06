# Repo, build, and accounts

Facts from README.md, docs/source.md, docs/project-layout.md, docs/README.md, docs/gh-vs-hub.md, and docs/multiple-accounts.md at 17142e08, rewritten in own words.

## Project layout

Top areas of `github.com/cli/cli`:

- `cmd/`: main packages for binaries such as `gh`.
- `pkg/`: most packages including per-command implementations.
- `docs/`: maintainer and contributor docs.
- `script/`: build and release scripts.
- `internal/`: highly specific internal packages.
- `go.mod`: external Go dependencies fetched at build time.

Historical top-level helpers: `api/` for GitHub API requests, `context/` DEPRECATED for git remotes only, `git/` for local repo info, `test/` DEPRECATED do not use, `utils/` DEPRECATED for table output only.

Help text lives in command source: `pkg/cmd/<command>/<subcommand>/<subcommand>.go`, as in `pkg/cmd/issue/list/list.go` for `gh issue list`. General topics live in `pkg/cmd/root/help_topic.go`. Release tooling in `cmd/gen-docs/main.go` converts them to manual pages at `https://cli.github.com/manual/`.

## Agent skill install

Install or update the gh agent skill with the built-in command:

- Install at user scope: `gh skill install cli/cli gh --scope user`.
- Update after a release: `gh skill update gh`.

User scope is recommended. Never copy a skill file by hand.

## Build from source

Steps from docs/source.md:

1. Check toolchain `Go 1.26+` with `go version`. Install from the Go website if missing.
2. Clone: `git clone https://github.com/cli/cli.git gh-cli`, then `cd gh-cli`.
3. Unix install: `make install` defaults to `/usr/local` (sudo may be needed), or `make install prefix=/path/to/gh` for another location.
4. Windows build: `go run script/build.go` produces `bin/gh.exe`. There is no install step on Windows; run `bin/gh version` to check.
5. Cross-compile with `GOOS`, `GOARCH`, `GOARM`, `CGO_ENABLED`, as in `GOOS=linux GOARCH=arm GOARM=7 CGO_ENABLED=0 make clean bin/gh` on Unix, or args to `go run script/build.go clean bin/gh GOOS=linux GOARCH=arm GOARM=7 CGO_ENABLED=0` on Windows. List targets with `go tool dist list`.
6. Confirm with `gh version`. Measured toolchain on this PC: `gh version 2.88.1 (2026-03-12)`.
7. Optional size trim: `GO_LDFLAGS="-s -w"` omits debug symbol tables.

## gh versus hub

`hub` behaves as a proxy to `git`; `gh` is a standalone tool. `gh` started fresh in early 2020 without ten years of hub design constraints and without aliasing to `git`, aiming to be opinionated and focused on GitHub workflows. Use `hub` when a git wrapper is wanted; use `gh` for opinionated GitHub workflows. `gh` is official and maintained by a GitHub team with support and issue tracking; `hub` is unofficial, maintained in spare time, and continues as long as it receives contributions. `gh` is not an exact replacement for `hub` and likely never will be.

## Multiple accounts

Since v2.40.0 `auth login` is additive: several accounts can sit under one host and the active one is switched with `auth switch`. Switching swaps the token for API requests and for git when `gh` is the credential manager.

- `auth status` shows each account with active flag, protocol, token, and scopes.
- `auth switch` changes the active account for the host.
- `auth token --user <name>` prints one account token, handy as `GH_TOKEN=$(gh auth token --user williammartin) gh api /user`.
- `auth logout` prompts when several accounts exist and switches to a remaining account when the active one leaves.
- `auth refresh -s <scope>` or `-r <scope>` amends scopes for the active user; finishing the browser flow as a different user errors instead of storing a mismatched token.
- Out of scope: automatic switching by directory or remote, automatic `user.name` or `user.email` setup, per-user editor config.
- Sharp edges: one-time `hosts.yml` migration with a new `version` field in `config.yml` (immutable-config users add `version: 1`); insecure-storage forward case uses an older token; GHES device-flow account picker may require pre-authenticating in the browser.

## Pins and licence

- Repo: `https://github.com/cli/cli`, default branch `trunk`, licence `MIT` (spdx `MIT`, LICENSE blob sha `b6a58a9572cbd7e4550f8205a9c4fd199cd442f2`).
- Pin: commit `17142e08db2e300b37e6da1ddcfb651eb6d9c587` on trunk, committer date `2026-10-05T16:25:07Z`, pushed 2026-10-06.
- Files: 10 files in `work/gh-cli-manual/src/` with board sha256 prefixes, including `source.md` download sha256 prefix `ac46c3d230cf` and contents-API blob sha `4f9506774b839969f4b790e841d3daf5d6d642cd` size 1709.
