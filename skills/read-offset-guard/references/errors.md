# Error lines the pairs replay (all thrown live by scripts/run_offset.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the clamped report instead.

- `Offset 100 is out of range for this file (50 lines)`: stale count read at offset 100. Pair `ro-count`
- `Offset 600 is out of range for this file (470 lines)`: stale length read at offset 600. Pair `ro-stale`
- `Offset 28 is out of range for this file (27 lines)`: one-past-the-end read at offset 28. Pair `ro-past-end`
- `Offset 88 is out of range for this file (45 lines)`: limit overshoot read at offset 88. Pair `ro-overshoot`
- `Offset 170 is out of range for this file (31 lines)`: blind jump read at offset 170. Pair `ro-jump`
- `Offset 150 is out of range for this file (19 lines)`: no-limit read at offset 150. Pair `ro-nolimit`
- `Offset 40 is out of range for this file (7 lines)`: guessed section read at offset 40. Pair `ro-head`
- `Offset 25 is out of range for this file (7 lines)`: past-the-head jump at offset 25. Pair `ro-first`
- `Offset 90 is out of range for this file (7 lines)`: walk past the end at offset 90. Pair `ro-walk`
- `Offset 8 is out of range for this file (7 lines)`: one-past-the-end read at offset 8. Pair `ro-tail`
- `Offset 60 is out of range for this file (5 lines)`: changed-file read at offset 60. Pair `ro-recount`
- `Offset 70 is out of range for this file (7 lines)`: unreported read at offset 70. Pair `ro-report`
- `Offset 315 is out of range for this file (44 lines)`: deep jump read at offset 315. Pair `ro-deep44`
- `Offset 90 is out of range for this file (32 lines)`: past-the-end read at offset 90. Pair `ro-queue32`
- `Offset 600 is out of range for this file (542 lines)`: long-index read at offset 600. Pair `ro-index542`
- `Offset 620 is out of range for this file (541 lines)`: long-index read at offset 620. Pair `ro-index541`
- `Offset 30 is out of range for this file (28 lines)`: just-past-the-end read at offset 30. Pair `ro-handoff28`
- `Offset 180 is out of range for this file (133 lines)`: board read at offset 180. Pair `ro-board180`
- `Offset 600 is out of range for this file (544 lines)`: long-index read at offset 600. Pair `ro-index544`
- `Offset 1997 is out of range for this file (0 lines)`: empty-file read at offset 1997. Pair `ro-empty0`
- `Offset 135 is out of range for this file (133 lines)`: just-past-the-board-end read at offset 135. Pair `ro-handoff135`
- `Offset 600 is out of range for this file (534 lines)`: long-index read at offset 600. Pair `ro-index534`
- `Offset 620 is out of range for this file (547 lines)`: long-index read at offset 620. Pair `ro-index547`
