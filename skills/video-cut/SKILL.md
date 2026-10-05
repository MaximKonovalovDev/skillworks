---
name: video-cut
description: Turn clips plus music into a beat cut, 3 vertical shorts, and captions. Use when the buyer wants a finished short-form pack from raw footage.
license: MIT
---

# video-cut

Buyer gets: one beat cut + three 9:16 shorts + captions burned in.

## Inputs

- `brief.md`: one line title, target length, song name.
- `clips/`: video files, in shoot order.
- `music.wav` or `music.mp3`: one track.

## Chain (mirrors video-studio)

1. Beat grid:
   `python tools/beat/detect.py music.wav`
   `node tools/beat/grid.mjs --selftest`
2. Timeline + free-app file:
   `node --input-type=module -e "import{timelineToOsp}from'./adapters/osp.mjs';await timelineToOsp('timeline/timeline.json','cut.osp')"`
3. Render long cut + shorts crop:
   `node tools/render/proof30.mjs`
   `ffmpeg -y -i full.mp4 -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" -c:a copy shorts.mp4`
4. Captions (offline whisper, broadcast-safe SRT):
   `ffmpeg -y -i shorts.mp4 -vf "subtitles='out.srt'" -c:a copy captioned.mp4`
   `ffprobe -v quiet -print_format json -show_format -show_streams captioned.mp4`
5. Publish list only:
   `node publish/publish.mjs --selftest`

## Outputs

- `cut.osp`: timeline for the free viewer.
- `full.mp4`: long beat cut.
- `shorts/`: three captioned 9:16 mp4 files + `out.srt`.

## Limits

- No Adobe apps, no Premiere/DaVinci/AE calls.
- No GPU, no cloud render. ffmpeg CPU only.
- Offline first: missing clips, music, or binary stops with ERROR, no stub output.
