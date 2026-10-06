# Syntax and commands

Facts from docs/command-line-syntax.md and docs/command-development.md at 17142e08, rewritten in own words.

## Syntax marks

- Literal text: plain text for fixed parts, as in `gh help` where `help` is required.
- Placeholder values: angled brackets for a user-supplied value, as in `gh pr view <issue-number>`. No other expression inside the brackets.
- Optional arguments: square brackets, as in `gh pr checkout [--web]`. Mutually exclusive optionals separate with vertical bars: `gh pr view [<number> | <url>]`.
- Required mutually exclusive arguments: braces with vertical bars, as in `gh pr {view | create}`.
- Repeatable arguments: ellipsis, as in `gh pr close <pr-number>...`.
- Variable naming: dash-case for multi-word variables, as in `<issue-number>`.
- Combined shapes: `command sub-command [<arg>]`, `command sub-command {<path> | <string> | literal}`, `command sub-command [<path> | <string>]`.

## Command layout

A command `gh foo bar` lives in `pkg/cmd/foo/bar/` with `bar.go`, `bar_test.go`, and optional `http.go`/`http_test.go`. Keep command-local logic there; check for a family `shared` helper before adding a global API.

Named patterns:

- `ListOptions` and `NewCmdList` in `pkg/cmd/issue/list/list.go`: Options hold flags and dependencies; constructor takes `*cmdutil.Factory` and injectable `runF`.
- `listRun`: run function owns business logic; `RunE` dispatches to `runF` when supplied.
- `New` in `pkg/cmd/factory/default.go`: shared dependency wiring.
- `NewCmdRoot` in `pkg/cmd/root/root.go`: top-level registration.
- `NewCmdIssue` in `pkg/cmd/issue/issue.go`: subcommand registration with `cmdutil.AddGroup`.

Entry: `cmd/gh/main.go` main delegates to `ghcmd.Main` in `internal/ghcmd/cmd.go`, building the tree through `root.NewCmdRoot`. Typical run: `go run script/build.go`, then `bin/gh issue list --limit 5`, dispatch from root to `RunE` in `pkg/cmd/issue/list/list.go`, flag parsed into `opts.LimitResults`, `listRun` runs, output via `opts.IO` streams in `pkg/iostreams/iostreams.go`, exit 0 on success.

## Flags, help, errors

Reuse `pkg/cmdutil/flags.go` helpers: `NilStringFlag` and `NilBoolFlag` separate omitted from explicit empty or false; `StringEnumFlag` gives enum validation and completion. Keep accepted values, defaults, names, and non-interactive paths.

Write examples with `heredoc.Doc`, `#` comment lines, `$ ` prefixes. Edit help in command Go source or `pkg/cmd/root/help_topic.go`, never in generated manual pages.

Error helpers in `pkg/cmdutil/errors.go`: `FlagErrorf` for bad flags with usage, `MutuallyExclusive` for conflicting flags, `SilentError` for exit 1 with no extra message, `CancelError` for user cancel, `PendingError` for pending outcome, `NoResultsError` and `NewNoResultsError` for empty results.

## Output and scriptability

Keep script contracts stable: flags, arguments, defaults, exit behavior, error messages, JSON fields, non-TTY output, stdout and stderr routing. Use `pkg/iostreams/iostreams.go` for TTY detection, color, and pager; `internal/tableprinter` for tables. Data stays on stdout, diagnostics on stderr. Non-TTY tables are script-friendly with no truncation, color, or headers. Every prompt needs a non-interactive flag path.

Structured output: `cmdutil.AddJSONFlags` in `pkg/cmdutil/json_flags.go` adds `--json`, `--jq`, `--template`. In the run function return `opts.Exporter.Write(opts.IO, data)` when set, before human output. Keep JSON field names, types, and empty-result behavior.
