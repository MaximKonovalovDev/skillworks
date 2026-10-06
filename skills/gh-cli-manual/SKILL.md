---
name: gh-cli-manual
description: Use when calling GitHub through gh CLI with host-aware routing, repo-record-first reads, explicit-host precedence, api_host gateway scope, or gh command syntax: host selection, token routing, CLI quoting, and pinned-ref API calls with the exact commands to type.
version: 0.1.0
author: skillworks
license: MIT
---

# gh CLI manual distilled

Fix-first rules distilled from cli/cli at 17142e08 (trunk, 2026-10-05) for the doctor GitHub-call class: which host an operation targets, which traffic a gateway reroutes, which syntax mark to type, and which gh api call proves the pin. Each rule names the exact token to type and the output fragment that proves it. Detail lives in references/host-routing.md, references/syntax-commands.md, and references/repo-build.md; terms in references/glossary.md, recipes in references/patterns.md, one-page reminder in references/cheatsheet.md.

## Host selection first

- Resolve a repository-scoped operation through the command selection path then use `repo.RepoHost()`; respect an `explicit host flag` and its validation instead of replacing it; use `cfg.Authentication().DefaultHost()` only when the operation needs a configured default [src: docs/api-and-hosts.md]
- Treat `ghinstance.Default()` as the constant `github.com`, never as user-selected host resolution; check for an explicit or repository host before touching it and never replace it with `DefaultHost()` mechanically [src: docs/api-and-hosts.md]

## Gateway scope

- Apply `api_host` to `API traffic only`; it is a `per-host` entry in `hosts.yml`, so one host can route through `gh-gateway.example.com` while another goes direct [src: docs/api-host.md]
- Keep git operations, browser URLs, and OAuth device flow on the host itself; an API gateway never replaces the repository host for login, remotes, or web URLs.
- Name `gh api` a wart worth naming: it carries a `second implementation` of the routing rule because it takes its path `verbatim` from the user and cannot go through the `go-gh` client, so never assume one implementation covers everything [src: docs/api-host.md]

## Syntax and tool choice

- Write placeholders in `angled brackets` as `<issue-number>`, optional arguments in `square brackets` as `[--web]`, required mutually exclusive choices in `braces` as `{view | create}`, and repeatable arguments with an `ellipsis` as `<pr-number>...` [src: docs/command-line-syntax.md]
- Treat `hub` as a `proxy to git` for git-shaped work and `gh` as a `standalone` `opinionated` tool for GitHub workflows; never call `gh` a proxy to git and never call it an exact hub replacement [src: docs/gh-vs-hub.md]
- Install the agent skill with `gh skill install cli/cli gh --scope user` at `user scope` and refresh it with `gh skill update gh` after each release; never copy a skill file by hand and never skip update after release [src: README.md]

## Build and prove the pin

- Build from source with toolchain `Go 1.26` checked by `go version`, clone `cli/cli`, run `make install` on Unix, build `bin/gh.exe` with `go run script/build.go` on Windows where there is no install step, cross-compile with `GOOS` plus `GOARCH`, and confirm with `gh version` [src: docs/source.md]
- Prove the licence with `gh api repos/cli/cli --jq` reading `MIT` spdx id and `trunk` default branch; anything else means the pin moved [src: README.md]
- Prove the pin with `gh api repos/cli/cli/commits/trunk --jq` reading `17142e08db2e300b37e6da1ddcfb651eb6d9c587` and `2026-10-05`; a `main branch` label or a guessed SHA fails the check [src: docs/README.md]
- Prove the pinned file with `gh api repos/cli/cli/contents/docs/source.md?ref=17142e08` reading the blob `sha` for `source.md`; the local download sha256 starts `ac46c3d230cf` and a `404` means a guessed raw URL [src: docs/source.md]
- Report the measured toolchain with `gh --version` printing `2.88.1`; never reinstall to check and never read the version from a screenshot [src: README.md]

## Fix-first workflow

Start from the symptom and apply one section above: a wrong host needs the host-selection rule, a gateway miss needs the gateway-scope rule, a syntax dispute needs the syntax rule, a hub-versus-gh debate needs the tool-choice rule, a stale install needs the build rule, and a licence or pin doubt needs the prove-the-pin rules. Per-symptom recipes are in references/patterns.md and the one-page reminder is in references/cheatsheet.md.
