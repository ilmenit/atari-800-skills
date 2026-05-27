---
name: atari8bit-antic-dli-ref
description: >-
  Deep DLI reference for Atari 8-bit ANTIC — full boilerplate, shadow-vs-hardware register gotchas, VSCROL deadline table, JVB storm rule, rainbow marching kernel, multi-mode zone patterns (HW-assisted vertical parallax, GTIA 9++ DCTR kernel), NVBL deferred VBI return. Use when writing or debugging DLI-based colour changes, P/M multiplex bands, DLI storms on JVB, or GTIA 9++/HIP-mode split kernels.
---

# references/antic-dli — DLI Deep Reference

---

## Purpose

This file is a tier-3 deep-dive supplement to antic.md (§§3.6/3.8/3.10). When an agent has exhausted the main §3.6 DLI boilerplate and §3.8 multiple-DLI patterns and still has timing bugs, wrong register writes, or NMI storm crashes, load this file. Covers every gotcha that bites in practice: shadow-vs-hardware, VSCROL deadline table, JVB stack-depth limit, rainbow marching, and two heavy case-studies: (a) HW-assisted vertical parallax DLI chain, (b) GTIA 9++ DCTR VSCROL kernel.

---

## Quick-Lookup

| Need | See § |
|---|---|
| Mandatory PHA/TXA/PHY/PLA/RTI boilerplate | §1 |
| Shadow vs hardware register table (PRIOR/COLPFn) | §2 |
| VSCROL deadline table (cycle 0/108/5) | §2.1 |
| JVB DLI storm — stack depth limit | §3 |
| Rainbow / colour-march on blank-line ROR | §4.4 |
| HW vertical parallax DLI band chain | §4.1 |
| GTIA 9++ DCTR VSCROL timing kernel | §4.2 |
| ORA overlapping scanline RMW pattern | §5 |
| NVBLNV deferred VBI return (SETVBV/XITVBV) | §6 |

---

## §1  Mandatory DLI Boilerplate

The shortest correct DLI that changes one hardware register:

```asm
my_dli
        pha                 ; save A
        txa
        pha                 ; save X
        tya
        pha                 ; save Y

        sta WSYNC           ; wait for end of current scan line
        lda #$0C
        sta COLPF0          ; $D016 — hardware, not $02C4

        pla
        tay
        pla
        tax
        pla
        rti                 ; pops P register from stack
```

**The RTI path:** the OS handler at $FFFA passes control to the handler at address loaded into `VDSLST ($200/$201)`. On entry, the CPU has already pushed the P register; RTI pops it off the stack — that is the `I`-flag restore that re-enables / disables IRQ.

**Do not skip PYA/Y/PLA/PLY in the prologue/epilogue.** Relying on the DLI being in a band that preserves X/Y, or that the OS has stored A, is a fragile assumption — the behaviour differs between OS-A/XL/XE and bare-metal.

---

## §2  Shadow-vs-Hardware Register Gotcha

The OS maintains shadow registers in page 2 (e.g. `PCOLR0=$02C0`, `COLOR0=$02C4`, `GPRIOR=$022E`). Every VBI the OS copies every shadow register to its corresponding hardware register. Changes to shadow registers *during a DLI* are NOT reflected in hardware until the next VBI.

**Rule:** write to `$D0xx` hardware registers in DLI; write to `$02xx` shadow registers only in VBI or main code.

### POKEY Timer IRQ Scanline Split

The MADS examples usually named `irq_mcp.asm` and `irq_mcp_2.asm` show a useful alternative to very long DLI chains: use the DLI to land at a stable scanline, then arm a POKEY timer IRQ for an intra-line colour split.

```asm
dli_arm_irq
        pha
        txa
        pha

        lda #0
        sta SKCTL              ; stop keyboard scan while aligning timer
        sta WSYNC              ; stable scanline boundary
        ldx #20
?wait   dex
        bne ?wait
        sta STIMER             ; reset POKEY timers at known cycle
        lda #1
        sta SKCTL              ; restore keyboard scan
        lda #4
        sta IRQEN              ; enable selected POKEY timer IRQ

        pla
        tax
        pla
        rti
```

Use this for MCP/HIP/RIP-style colour timing where a normal DLI cannot hit the exact horizontal position cheaply. Always restore `SKCTL`, acknowledge/disable `IRQEN` in the IRQ stop path, and keep the custom IRQ vector resident outside any banked `$4000-$7FFF` window.

### Shadow → Hardware mapping

| Shadow ($02xx) | Hardware ($D0xx) | Notes |
|---|---|---|
| `PCOLR0 = $02C0` | `COLPM0 = $D012` | colour / |
| `PCOLR1 = $02C1` | `COLPM1 = $D013` | use hardware register in DLI |
| `PCOLR2 = $02C2` | `COLPM2 = $D014` | |
| `PCOLR3 = $02C3` | `COLPM3 = $D015` | |
| `COLOR0 = $02C4` | `COLPF0 = $D016` | PF0–3 + BAK |
| `COLOR1 = $02C5` | `COLPF1 = $D017` | |
| `COLOR2 = $02C6` | `COLPF2 = $D018` | |
| `COLOR3 = $02C7` | `COLPF3 = $D019` | |
| `COLOR4 = $02C8` | `COLBK = $D01A` | background / border |
| `GPRIOR = $022E` | `PRIOR = $D01B` | P/M priority bits |
| `CHACT = $02F1` | `CHACTL = $D401` | character mode control |
| `CHBAS = $02F4` | `CHBASE = $D409` | character set base |

---

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

---

## §3  JVB DLI Storm — Stack Depth Limit

`$41` (JVB) is re-executed once per scan line in the range scan-line 8–248. Every scan line an NMI fires, pushes the stack, and DLI handler runs. **Maximum ≈25 concurrent DLIs before the 6502 256-byte stack overflows** (runaway cascades if the DLI cascade writes more than it pops per frame).

**Mitigation:**

```asm
; DLI storm guard — only run on every Nth scan line
storm_counter = $90
storm_threshold = $05       ; execute 1/5 of JVB DLIs

jvb_dli
        pha
        txa
        pha
        tya
        pha

        inc storm_counter
        lda storm_counter
        cmp #storm_threshold
        bne ?skip            ; skip all but every 5th DLI
        ; -- critical DLI work here --
        lda #$00
        sta COLPF0
?skip
        pla
        tay
        pla
        tax
        pla
        rti
```

Alternatively, use `NMIEN bit 7` gating: disable DLI output on the last DLI of the JVB frame before the VBI fires. On next VBI, re-enable. DLI storm is a tool (used by the `unity` demo for the 3-mode scan-line split), not a bug — just guard the stack.

---

## §4  Multi-Zone DLI Patterns

### §4.1  HW Vertical Parallax Band Chain (VBI pre-sets + DLI swaps)

For "psuedo-side-scrolling" where sky / mid-ground / foreground scroll at different rates:

```asm
        ; VBI pre-computes scroll positions for 12 bands × 4 players
band_hpos = $60           ; 12 × 2 = 24 bytes direct page (HPOS L/H per band)
band_color = $78          ; 12 * 2 bytes      

vbi_parallax
        pha
        txa
        pha
        tya
        pha

        ; --- update sky band 0 — no scroll every frame ---
        lda #$80            ; HPOS0 for sky 
        sta band_hpos

        ; --- update scroll offset for band i (accumulates each frame) ---
        lda scroll_offset
        adc band_speed,x    ; band_speed LUT: 0=sky, 2=mid, 4=fg
        sta band_hpos+12,x

        ; --- install DLI band chain ---
        lda #<band_dli_0
        sta VDSLST
        lda #>band_dli_0
        sta VDSLST+1

        lda #NMIEN_VBI | NMIEN_DLI
        sta NMIEN

        pla
        tay
        pla
        tax
        pla
        rti

; --- band_i DLI (one per band, page-aligned to save 6 cycles) ---
band_dli_0 *= $2100       ; page-aligned
        pha
        txa
        pha
        tya
        pha
        lda band_hpos      ; HPOS L/H from pre-computed LUT
        sta HPOSP0         ; $D000
        lda band_color     ; COLPF? for this band
        sta COLPF0         ; $D016
        pla
        tay
        pla
        tax
        pla
        rti

band_dli_1 *= $2200       ; next page, next band
        ; ... same pattern with band i+1 colour/position
```

**Key design points:**
- Bands must be page-aligned (`*= $2N00`) to save 6 cycles vs 16-bit pointer reload per band.
- Precompute band LUTs in VBI (not in DLI — DLI has very few cycles).
- VBI pushes band positions into page-zero LUT so DLI only reads a single `LDA / STA` pair.

### §4.2  GTIA 9++ — DCTR VSCROL Timing Kernel

GTIA 9++ (GTIA Mode E with DCTR-driven line-repeat): using VSCROL trick to repeat each scan-line as 4 pixel-rows, producing a 32-pixel-high (160-wide) display from only one mode-line half the ROM. Split kernel:

```asm
; VSCROL values at DCTR boundary:
;   DCTR=13 → VSCROL=13 held at end of line → next row-counter = 3 (drops to 4 of 16)
;   DCTR=3  → VSCROL=13 on NEXT line → DCTR counts 3→15, 14 rows (wraps) → ~4 rows/line
;   net result: each real scan line = 4 pixel rows

; DLI fires at the boundary between two DCTR cycles — the only safe moment
; to update VSCROL without disrupting the DCTR counter mid-run

gtia9pp_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC                       ; land at scan line boundary
        lda #$03                        ; DCTR = 3 → only 4 rows visible at end
        sta VSCROL                      ; $D405 — now DCTR counts 3,4,5,6…14,15 wraps
        ; note: only 4 rows shown (3,4,5,6) then next scan line rereloads
        ; 13 rows skipped in the missing 12 rows for next boundary
        nop                             ; wait --- 13 CPU cycles = 13/4 = 3.25 cycle-wrap
        lda #$0D                        ; set to 13 for next repetition to start
        sta VSCROL                      ; next: DCTR counts 13,14,15,0 → 4 rows again

        ; Optional: alternate PRIOR between $40 (mode 9) / $00 (mode F base)
        lda #$40                        ; GTIA 9
        sta PRIOR                       ; $D01B
        ; next DLI on next scan line does the same, alternating

        pla
        tay
        pla
        tax
        pla
        rti
```

**DCTR state diagram (one full VSCROL cycle through one pair of mode lines):**

```
Row-counter: 13 →14 → 15 →  [wrap @0] → 0 → 1 → 2 → 3 -- VSCROL=13->3--> -- next-VSCROL@13--row-count 3→15 wrap 4-pixel-row visible
```

**Cycle budget inside the DLI:**
```
PHA/TXA/PHY    =  6 cycles
WSYNC          =  7 cycles (CPU halts until cycle 105)
LDA #0 / STA VSCROL =  4+4 =  8 cycles
...NOPs        = 13 cycles (fill to align DCTR boundary)
LDA #1 / STA VSCROL =  8 cycles
LDA #$40 / STA PRIOR = 8 cycles
PLA/PLX/PLA/RTI     = 16 cycles
TOTAL          ≈ 57 cycles — fits in ~97 cycles/line on Mode E
```

**Caveats:**
- VSCROL cannot be written at scan line 240+ (JVB wraps — use `CMP VCOUNT` to detect before writing).
- DCTR is not directly readable; verify the DLI by counting how many rows are shown on a test pattern.
- Mid-frame LMS at scan line 95 on a 192-line Mode E kernel can disrupt VSCROL — guard with `CMP VCOUNT` at boundary.

---

## §5  ORA Overlapping Scanline-RMW Pattern

From ironman.md §Soft Sprites → ORA overlapping for colour: two players overlaid on the *same scan line* produce a colour where the OR of their masks falls:

```asm
        ; Two 1-bit players, same Y-band
        ; P0 = left-half colour; P1 = right-half colour
        ; → left half = P0; right half = P1; overlap = P0|P1

player0_mask: .byte $FF,$00,$FF,$00   ... ; 8 scan lines, alternating colour
player1_mask: .byte $00,$FF,$00,$FF   ... ; shifted by 1 scan line

        ; GPRIOR = $01  (player 0 over playfield; player 1 ALSO over playfield)
        ; No 5th-player trick here — just raw ORA overlap

ora_dli
        pha
        txa
        pha
        tya
        pha

        sta WSYNC
        lda player0_mask,y
        sta GRAFP0              ; $D00D
        lda player1_mask,y
        sta GRAFP1              ; $D00E

        pla
        tay
        pla
        tax
        pla
        rti
```

**Practical type sizes for ORA overlap:**
- 1-bit mask (2 colors): use bit 0 = P0 colour, bit 1 = P1 colour → OR mask is 3-colour sprite with no fifth player needed
- Extend to 3 players (6-colour sprite) by adding P2 at bit 2 in a shared mask table

---

## §6  NVBLNV — Deferred VBI via SETVBV/XITVBV

From scrolling.md. The VBI entry point `XITVBV` is set up by `SETVBV` before the VBI fires for the first time, and every subsequent VBI must return via `XITVBV` rather than `RTI` so the OS restores the VIM accumulator and completes the OS-IRQ chain.

```asm
        ; Register deferred VBI (do this ONCE at startup)
        ldx #>vbi_deferred
        ldy #<vbi_deferred
        lda #$07               ; 7 + NMIEN_VBI = deferred vertical blank
        jsr SETVBV             ; $E45C XL/OS vector — installs vector in VIM

vbi_deferred
        pha
        txa
        pha
        tya
        pha

        ; ... VBI work ...

        jmp XITVBV             ; $E462 — restores A/X/Y; exits deferred VBI through OS
```

**Why NVBLNV matters for DLI-heavy demos:** `RTI` from a VBI restores the I flag (which was clear) → IRQ mask off. `XITVBV` does the same via the OS path — but additionally re-arms the NMI enabler, so the next VBI / DLI chain continues uninterrupted. Forgetting to call `XITVBV` on the last instruction of a VBI with a looping DLI → the DLI tree stops on the next vertical blank.

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
