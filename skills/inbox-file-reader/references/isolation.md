# Isolation model

`file_one_item.py` touches exactly two files: it reads `--inbox` and
appends to `--board`. Nothing else is opened for read or write.

- One item = the first non-empty line of `--inbox`, stripped. Filing
  appends `- [ ] <item>` plus a newline to `--board` (created with
  parents when missing) and rewrites `--inbox` without that line.
- Path allowlist: `--inbox` and `--board` must each end in `.md`,
  `.markdown` or `.txt`. Any other suffix (notably `.py` code files)
  is refused: exit code 2, stdout starts `ERROR refused:`, and neither
  file is created, truncated, or appended to.
- `--inbox` and `--board` must not resolve to the same file; a
  self-filing pair is refused the same way, exit 2, nothing written.
- A missing or all-blank inbox is refused the same way (exit 2) and
  the board is left untouched — file one real item or file nothing.
- The success line on stdout is `FILED <item> -> <board>`, exit 0.
  Filing is single-item per run: rerunning files the next line.
