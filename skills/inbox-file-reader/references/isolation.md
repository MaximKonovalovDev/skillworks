# Isolation model

`file_one_item.py` touches exactly two files. It reads `--inbox` and the last bytes of `--board` (to keep that file's
line breaks), appends to `--board`, and rewrites `--inbox`. Nothing else is opened for read or write.

## Filing

- One item is the first non-empty line of `--inbox`, trimmed. Filing appends `- [ ] <item>` and a line break to
  `--board`, and rewrites `--inbox` without that line.
- The board keeps its own style: if it already holds a CRLF line break the new line ends with CRLF, otherwise LF. A new
  board uses LF. When the board's last line has no break, one is added before the new line.
- The board is created with its parent folders when it is missing. The inbox keeps every other line, including blank
  lines, its line breaks and a leading byte order mark, byte for byte.
- The success line on stdout is `FILED <item> -> <board>`, exit 0. Filing is one item per run: a rerun files the next
  line. If the board write fails the inbox is not changed; if the process stops between the two writes the item stays
  in the inbox and is filed again on the next run (a duplicate, never a loss).

## Refusals (exit 2, nothing written)

- Path allowlist: `--inbox` and `--board` must each end in `.md`, `.markdown` or `.txt`, in any letter case. Any other
  suffix, notably code files such as `.py`, is refused: stdout starts `ERROR refused:` and says `outside allowlist`,
  and neither file is created, truncated or appended to.
- `--inbox` and `--board` must not resolve to the same file, however the path is spelled: `ERROR refused: inbox and
  board are the same file`.
- A missing inbox: `ERROR inbox missing: <path>; board untouched`. The board and its folders are not created.
- An inbox with no non-blank line: `ERROR inbox empty: <path>; board untouched`.
- An inbox that is not UTF-8 text: `ERROR inbox is not UTF-8 text: <path>; board untouched`.
- A board that cannot be written: `ERROR cannot write board <path>: <reason>; inbox untouched`.
