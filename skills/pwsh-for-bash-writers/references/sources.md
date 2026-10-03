# Sources and licences (verified 2026-10-03)

The skill text and every example are written fresh. The pages below were read to check each rule. No page text is copied.

- PowerShell reference docs: https://github.com/MicrosoftDocs/PowerShell-Docs
  - Pinned commit: a3de8f22552170e70852470d46cd52cd9ca471ec (main, 2026-09-24), folder `reference/7.6/`.
  - Licence, read live from the repository root on 2026-10-03: `LICENSE.md` is Creative Commons Attribution 4.0 (CC-BY-4.0) for the documentation text. `LICENSE-CODE.md` is the MIT licence (Copyright Microsoft Corporation) for the code samples. The GitHub API reports "NOASSERTION" because the repository carries both files.
  - Pages used for the rules: `about_Quoting_Rules` (single and double quotes, here-strings), `about_Parsing` (argument mode, the stop-parsing token, native arguments), `about_Redirection` (the streams, `*>`, `$null`), `about_Pipeline_Chain_Operators` (`&&` and `||` need pwsh 7 and pipelines), `about_Automatic_Variables` (`$?`, `$LASTEXITCODE`), `about_Special_Characters` (backtick escapes), `Get-Content` (`-Tail`, `-TotalCount`), `Select-String`, `Get-Date` (`-AsUTC`), `Compare-Object`, `Start-Process`.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7.6.3), the exit codes and the hang timings in `servers.md` (Windows 10, Node 24.14).
- How the shell tool starts a command: OpenCode 1.18.34 runs `pwsh -NoLogo -NoProfile -NonInteractive -Command <text>`, read from the program's own code (the shell tool in the binary).

Credit line for THIRD_PARTY_NOTICES.md: MicrosoftDocs/PowerShell-Docs (CC-BY-4.0 text, MIT code), PowerShell reference, used as the checked source for the pwsh-for-bash-writers skill. Changes: rewritten, shortened, tested.
