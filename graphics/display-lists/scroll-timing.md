# Scroll Timing

## §2.1  VSCROL Deadline Table

The the reference manual §4.7 states three VSCROL write deadline windows:

| Deadline (cycle relative to scan line) | What happens if you miss it |
|---|---|
| Cycle 0 | VSCROL not yet latched → new count **not applied** this scan line |
| Cycle 108 | DCTR stop counter for *previous* scrolled line not updated → row-counter spirals off by 4 scan lines |
| Cycle 111 | VSCROL write MISSES the pipe until next scan line |

**Practical rule:** write VSCROL at cycle 0–5 of the desired scan line. In DLI, arrive via WSYNC to land exactly at cycle 105 (reprisable scan line start): `sta WSYNC → lda #n → sta VSCROL`.

### HSCROL write rules

| Rule | Explanation |
|---|---|
| All playfield-width rules apply | narrow→normal→wide expansion is automatic; HSCROL < 4 for narrow, < 4 for normal, < 8 for wide |
| GTIA 9/10/11 MUST use even HSCROL | GTIA pairs adjacent color-clock bytes into 4-bit pixels; odd shifts corrupt the pairing |
| Mid-line LSB write propagates immediately | writing HSCROL mid-scan line affects the left-visible edge without flicker; bits 1–3 change DMA fetch start/stop windows |
| Crossing DLI-trigger during write | if bit 1–3 change crosses the boundary where ANTIC must stop/start DMA, playfield corruption results — do HSCROL write only at HBLANK (WSYNC) |

## §2.2  Wide Playfield + HSCROL + VSCROL=0 Timing Gotcha

On the first scan line of a Mode 4 line with wide playfield and horizontal scroll enabled, ANTIC can leave roughly 10 CPU cycles before playfield DMA starts. A DLI placed on the last scrolled line with `VSCROL=0` can therefore be too late for useful work.

Main causes:

- Wide playfield fetches 48 bytes per line.
- Horizontal scroll adds the extra left/right scroll buffer fetch.
- Mode 4's first scan line also pays character/font fetch cost.

Mitigations:

| Option | Effect |
|---|---|
| Keep `VSCROL >= 1` on the DLI boundary | Gives the DLI a later scan-line window |
| Use normal-width playfield for the split | Removes wide-playfield DMA steal |
| Move the DLI target one scan line later | Avoids the first-line fetch burst |

```asm
vbi_end
        lda   vert_scroll
        ora   horz_scroll
        bne   ?ok
        lda   #1
        sta   VSCROL          ; floor avoids the VSCROL=0 first-line trap
?ok     jmp   XITVBV
```

---

## §7  VSCROL=0/1/2... LSB_WIDTH_TABLE

| VSCROL | First scrolled-mode-line scan lines rendered | Buffer-zone line scan lines rendered | Net line count (Mode 4 = 8) |
|---|---|---|---|
| 0 | 8 (0–7 all) | 1 (scan line 0) | 9 total — buffer = 1 scan line |
| 1 | 7 (1–7) | 2 (0–1) | 9 |
| 2 | 6 (2–7) | 3 (0–2) | 9 |
| 3 | 5 (3–7) | 4 (0–3) | 9 |
| 4 | 4 (4–7) | 5 (0–4) | 9 |
| 7 | 1 (7 only) | 8 (0–7) | 9 |

**Invariant:** the total number of scan lines output by the scrolled region + buffer-line pair is always 8+1=9 for Mode 4 — the distribution between the two is the only variable.

**VSCROL update cost: 6+4+4 bytes = 14 machine cycles.** Update in VBI or DLI only.

---

*This file is references/antic-dli.md — tier-3 supplement for antic.md §§3.6/3.8/3.10 and the embedded DLI / VSCROL deadline tables above remain in antic.md; only deep detail and extra patterns are archived here.*
