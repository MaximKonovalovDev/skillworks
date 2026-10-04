---
name: inbox-file-reader
description: File exactly one inbox line onto a board file and touch nothing else, with a path allowlist so code files can never be read or written. Use for autonomous triage of one inbox item into a board or inbox markdown file when everything else, especially code, must stay untouched; FILED on success, refused outside the allowlist.
license: MIT
---

# inbox-file-reader

File one inbox item, touch nothing else. Headless: no network, no prompts. It takes the first non-empty line of the
`--inbox` file, appends one checkbox line to the `--board` file and drops that line from the inbox.

## Use it

Run `scripts/file_one_item.py` from this skill's folder, or give its full path:

```powershell
python scripts/file_one_item.py --inbox <inbox.md> --board <board.md>
```

The first word of stdout is the answer. One item per run: run it again for the next line.

- `FILED <item> -> <board>`: exit 0. The board got `- [ ] <item>` as a new last line, the inbox lost that one line.
  Every other line of both files is unchanged, byte for byte, and no other file is opened.
- `ERROR refused: ...`: exit 2, nothing written. The path is outside the allowlist, or inbox and board are the same
  file.
- `ERROR inbox missing: ...; board untouched`, `ERROR inbox empty: ...; board untouched` (no non-blank line) and
  `ERROR inbox is not UTF-8 text: ...; board untouched`: exit 2, nothing written, no board folder is created.

## Rules

- The allowlist: both paths must end in `.md`, `.markdown` or `.txt` (any letter case). A `.py`, `.ps1`, `.json`,
  `.mjs` or extensionless path, on either side, is refused. This is the guard that keeps code untouched: do not
  work around it with a copy of the script.
- The board is created with its folders when it does not exist. An existing board keeps its own line breaks (CRLF or
  LF), and a last line without a break gets one first, so the new line never joins it.
- The item is the first non-empty line, trimmed. Blank lines stay where they are.
- It does not judge the item, deduplicate it or rewrite it. Triage means choosing the board; the choice is yours.

The two-file guarantee and the board line shape: `references/isolation.md`.
