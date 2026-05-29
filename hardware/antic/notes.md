# Notes

## 3.11  Emulator Accuracy Notes

| Behaviour | May differ in emulators |
|---|---|
| DLI overlap (6 DLI storms) | Some emulators do not implement full carry chain |
| JVB DLI at every scan line count | Exaggerated in some emulators |
| WSYNC cycle variance | Cycle-exact emulation varies; Altirra is most accurate |
| VSCROL timing / VCOUNT cycles | Old Altirra had off-by-one; fixed in 2022 |
| Mode 8/9 horizontal scroll bug (modes 2-5 at HSCROL≥10) | May produce visible garbage right-side of wide playfield |

---

## 3.12  Critical Warnings (Repeat)

1. **Never set NMIEN bit 7 before VDSLST is valid** — NMI vector must point to code before enabling.
2. **DLI must be short** — especially on JVB `$C1` (every scan line stacks: ~24 DLI frames).
3. **WSYNC before GTIA register write** — not after; you want the write near horizontal blank.
4. **Mode 4 first scan line** — only ~10 cycles available; don't WSYNC here.
5. **HSCROL on GTIA 9/10/11** — must be even for correct GTIA pixel pairing.
6. **VSCROL=0 with DLI enabled** — DLI fires on first scan line of next non-scrolled mode line, which in Mode 4 = only ~10 cycles; use VSCROL>0 or move DLI to later scan line.
7. **JVB display list maximum height = 240** — even in PAL; JVB itself uses one scan line (241 if you think you have 240 visible + JVB).

---

*All content is self-contained in this file; external sources embedded into §3.1–§3.6.*
