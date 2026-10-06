# gh-cli-manual glossary

Short meanings as the cli/cli docs use them. Quoted lines are the exact token the skill checks.

- RepoHost: `repo.RepoHost()` resolving the host of the selected repository.
- explicit host flag: a `--hostname` style flag or URL passed on the command line; its validation and precedence win over defaults.
- DefaultHost: `cfg.Authentication().DefaultHost()` returning the configured default host.
- Default: `ghinstance.Default()` always returning `github.com`; never user selection.
- factory: `factory.New` plus `HttpClientFunc` wiring config, auth, IO, and transport.
- api client: `api.NewClientFromHTTP` exposing `GraphQL`, `Query`, `Mutate`, and `REST`.
- api_host: per-host `hosts.yml` gateway entry rerouting API traffic only.
- HostForAPIHost: `api/http_client.go` mapping a gateway hostname back to its host for token lookup.
- go-gh: shared client library that owns request routing.
- verbatim: `gh api` taking its path exactly as the user typed it.
- angled brackets: `<name>` placeholder for a user-supplied value.
- square brackets: `[--flag]` marking an optional argument.
- braces: `{a | b}` marking required mutually exclusive choices.
- ellipsis: `...` marking a repeatable argument.
- hub: proxy to `git` for git-shaped work.
- standalone: `gh` running its own commands instead of wrapping `git`.
- opinionated: `gh` choosing one focused GitHub workflow.
- user scope: `gh skill install ... --scope user` installing the agent skill for the user.
- GOOS: cross-compile target OS variable; `GOARCH` is the CPU arch, `GOARM` the ARM version.
- trunk: default branch of cli/cli carrying the pin.
- blob sha: contents-API `sha` for a file at a ref, as `4f950677...` for docs/source.md.
