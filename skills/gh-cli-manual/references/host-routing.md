# Host routing and gateway

Facts from docs/api-and-hosts.md and docs/api-host.md at 17142e08, rewritten in own words. Short quotes only.

## Host-selection table

Three host sources, each with its resolver:

- Repository-scoped operation: resolve with the command existing selection path, then use `repo.RepoHost()`. Example carriers are `listRun`, `issueList`, `milestoneByNumber` in `pkg/cmd/issue/list/list.go`.
- Explicit host flag or URL: respect the command existing validation and precedence; do not replace it with a default. A default must not override a repository selected by `-R` or `GH_REPO`.
- Operation that needs a configured default: use `cfg.Authentication().DefaultHost()`, documented in `internal/config/config.go` as `AuthConfig.DefaultHost`.

## Default is not selection

`ghinstance.Default()` always returns `github.com`. It is not user-selected host resolution. Do not mechanically replace it with `DefaultHost()`: first determine whether the operation already has an explicit or repository host.

Delay repository and git discovery (`BaseRepo`, `Remotes`, `Branch`) until `RunE` or the run function. Bind `opts.BaseRepo = f.BaseRepo` inside `RunE` because `EnableRepoOverride` replaces `f.BaseRepo` in a pre-run hook; capturing the earlier function ignores `-R` and `GH_REPO`.

## Reuse clients

Get the configured HTTP client from the command dependency via `factory.New` and `HttpClientFunc` in `pkg/cmd/factory/default.go`. Wrap it with `api.NewClientFromHTTP` in `api/client.go` and reuse `GraphQL`/`Query`/`Mutate` and `REST`. Pass the chosen host and a relative API path. Keep endpoint headers, scopes, redirect policy, error handling, and pagination through the shared abstractions. Request only fields the command needs.

## api_host scope

`api_host` sends one host API traffic somewhere other than that host usual endpoint, so an org can front GitHub with a gateway:

- Config in `hosts.yml` per host: `github.com:` with `api_host: gh-gateway.example.com`. Then `gh api repos/cli/cli` asks the gateway, not `api.github.com`.
- Scope is API traffic only. Git operations, browser URLs, and OAuth device flow keep using the host itself.
- Per-host, not global: one host can route through a gateway while another goes direct.
- Same `api_host` on two hosts is a misconfiguration: the reverse lookup returns the first matching host with no error.
- Credentials: `api/http_client.go` maps the gateway back via `HostForAPIHost` so the host token is sent. The fallback only adds a token where there would have been none.

## Known gaps

Routing lives in `go-gh`, which reads `api_host`. Not yet central: some call sites still build absolute `https://api.github.com/...` URLs and bypass the gateway. `gh api` is a wart worth naming: it does not use the go-gh client, so it resolves `api_host` itself with a second implementation of the same rule, because it takes its path verbatim from the user. Release-asset upload and download go through `DoRequest` with an API-supplied absolute URL. Whole commands remain unmigrated and outside the harness: `gh codespace`, `gh agent-task`, `gh copilot`, and the update checker.
