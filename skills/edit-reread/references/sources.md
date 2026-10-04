# Sources and licences (verified 2026-10-04)

The skill text and every pair are written fresh. The pages below were read to check each rule. No page text is copied.

- PowerShell-Docs about_Parsing (CC-BY-4.0 text, MIT code samples, read live 2026-10-04).
  - Doc URL read live: https://raw.githubusercontent.com/MicrosoftDocs/PowerShell-Docs/staging/reference/7.4/Microsoft.PowerShell.Core/About/about_Parsing.md
  - Licence: CC-BY-4.0 for prose plus MIT for code samples per the MicrosoftDocs PowerShell-Docs repo (row DR-1004-2 provenance read live 2026-10-03).
  - Sections used for the rules: expression mode vs argument mode (why guessed oldString misparses), handling special characters (backtick escapes), line continuation (trailing spaces break edits).
- PowerShell-Docs about_Special_Characters (CC-BY-4.0 text, MIT code samples, read live 2026-10-03 per row DR-1004-2).
  - Doc URL: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_special_characters
  - Sections used for the rules: tabs vs spaces, trailing whitespace, CRLF vs LF line endings as exact bytes.
- Measured on this PC, not taken from a page: the pair results (`pairs.json`, pwsh 7), each bad side throwing the real stale-edit line of `target-class.json`.
- This skill is original work under MIT. It is free to use and share.

Credit line for THIRD_PARTY_NOTICES.md: edit-reread (MIT skill text and scripts; PowerShell-Docs CC-BY-4.0 text plus MIT code read live 2026-10-04, ideas only, no text copied).
