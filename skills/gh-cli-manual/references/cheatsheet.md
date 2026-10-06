# gh-cli-manual cheatsheet

One line per rule. Every line below matches a trial task in evals/gh-cli-manual_trials.jsonl.

Hosts: repo operation uses `repo.RepoHost()`; explicit `explicit host flag` wins; default is `cfg.Authentication().DefaultHost()`. (gm-a01)

Default: `ghinstance.Default()` returns `github.com`, never user selection; check explicit or repo host first. (gm-a02)

Gateway: `api_host` is `API traffic only`, `per-host` in `hosts.yml`; git, browser URLs, device flow keep the host. (gm-a03)

Wart: `gh api` carries a `second implementation` taking its path `verbatim`; shared client is `go-gh`. (gm-a04)

Syntax: `angled brackets` placeholders, `square brackets` optionals, `braces` exclusive required, `ellipsis` repeats. (gm-a05)

Tools: `hub` is `proxy to git`; `gh` is `standalone` and `opinionated`. (gm-a06)

Skill: `gh skill install cli/cli gh --scope user` installs at `user scope`; `gh skill update gh` refreshes. (gm-a07)

Build: `Go 1.26`, `make install`, `go run script/build.go` on Windows with no install step, `GOOS` plus `GOARCH`, check `gh version`. (gm-a08)

Licence: `gh api repos/cli/cli --jq` shows `MIT` and `trunk`. (gm-r01)

Pin: commits/trunk shows `17142e08db2e300b37e6da1ddcfb651eb6d9c587` and `2026-10-05`. (gm-r02)

File: contents for `source.md` at the pin shows blob sha; local sha256 starts `ac46c3d230cf`. (gm-r03)

Version: `gh --version` prints `2.88.1`. (gm-r04)
