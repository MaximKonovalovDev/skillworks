---
name: inbox-file-reader
description: Tiny isolated inbox reader that files one item to a board file and touches nothing else. Use for autonomous triage of one inbox line into an empire-inbox board when code files must stay untouched; FILED on success, refused outside the allowlist.
---

# inbox-file-reader

File one inbox item, touch nothing else. Headless: no phone, no
network, no prompts. Reads only the `--inbox` file, appends one board
line to only the `--board` file.

## Use it

```powershell
python skills/inbox-file-reader/scripts/file_one_item.py --inbox <inbox.md> --board <board.md>
```

- One item filed: prints `FILED <item> -> <board>`, appends
  `- [ ] <item>` to `--board`, drops the line from `--inbox`.
- Empty or missing inbox: prints `ERROR ...; board untouched`, exit 2.
- Path outside the allowlist (not `.md` / `.markdown` / `.txt`, e.g. a
  `.py` code file) or inbox == board: prints `ERROR refused: ...`,
  exit 2, nothing written.

The two-file guarantee and board line shape live in
`references/isolation.md`.
