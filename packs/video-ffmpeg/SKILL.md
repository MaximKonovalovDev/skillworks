---
name: video-ffmpeg
description: Thin ffmpeg verbs (cut, concat, overlay, clip) plus a log-tail prove step for small clip work.
---

# video-ffmpeg

Thin pack. It builds ffmpeg commands. It never runs ffmpeg.

## Verbs

- `cut(input, output, start, duration)`: one segment by start plus length.
- `clip(input, output, start, end)`: one range by start plus end.
- `concat(inputs, output)`: join 2 or more files into one.
- `overlay(base, over, output, x, y)`: lay one clip over a base at x:y.
- `log_tail(log, n)`: prove step. Returns the last n log lines plus PASS or FAIL.

## Prove step

Run from `packs/video-ffmpeg/`:

```powershell
python server.py --selftest
```

Green means `SELFTEST PASS`. After a real ffmpeg run, pass its log text to `log_tail`. FAIL means the tail holds an error line.

## Ideas

Verb ideas only from ffmpeg-mcp plus kinocut, both MIT. No code copied. Own rewrite. Licence: MIT.
