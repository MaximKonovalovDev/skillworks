# Cheatsheet: vivid-colors LS_COLORS theming

One page. Every line replayed from the sharkdp/vivid sources at `6f33cf1b`.

## Generate and enable

| See | Branch |
|---|---|
| who colors ls | `generator`, `LS_COLORS`, `vivid` |
| bash theme on | `export`, `vivid generate molokai`, `bashrc` |
| fish theme on | `set -gx`, `fish`, `vivid generate molokai` |
| old terminal | `--color-mode`, `8-bit`, `truecolor` |

## Palettes themes spec

| Want | Type |
|---|---|
| follow the terminal | `ansi`, `16-color`, `terminal theme` |
| add a theme | `themes`, `subfolder`, `explicit path` |
| molokai dirs/links | `cyan`, `pink`, `symlink` |
| write a color | `RRGGBB`, `24-bit`, `dircolors` |

## Lines

| Want | Type |
|---|---|
| generator claim | `LS_COLORS` 9 lines, first at line `6` with the generator |
| foreground claim | `foreground` 23 lines, first at line `27` with cyan |
| generate claim | `vivid generate` 5 lines, first at line `36` with molokai |
| depth claim | `8-bit` 5 lines, first at line `15` with RRGGBB |

## Prove the pin

| Replay | Prints |
|---|---|
| `rg -n "LS_COLORS" work/vivid-colors/src/README.md` | 9 match lines, first at line `6` with the generator |
| `rg -n "foreground" work/vivid-colors/src/molokai.yml` | 23 match lines, first at line `27` with cyan |
| `rg -n "vivid generate" work/vivid-colors/src/README.md` | 5 match lines, first at line `36` with molokai |
| `rg -n "8-bit" work/vivid-colors/src/README.md` | 4 match lines, first at line `16` with 8-bit codes |
