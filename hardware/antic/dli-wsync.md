# Dli Wsync

## 3.6  DLI — Full Reference

### Pre-Topic DLI Crash-Course (from playermissile.com)

The NMI path: `$FFFA → OS NMI dispatcher → VDSLST user vector ($200/$201)`. OS NMI handler saves PSR (but not A/X/Y — user handler must save them).

```
NMIEN ($D40E)   : $40 = VBI enable, $80 = DLI enable
NMIEN must be written by cycle 7 to ENABLE, cycle 8 to DISABLE.

VDSLST          : set this BEFORE writing NMIEN bit 7 ($80)
VDSLST+2 (=NMIRES): write $FF to clear DLI NMI flag (optional; not needed after boot)

RTCLOK+2 ($14)   : increments once per VBI — use to gate VBI-rate work
WSYNC ($D40A)   : write any value; CPU waits ≈cycle 105/114
```

**DLI can be shorter than a full scan line:** ANTIC fires DLI at the *beginning* of the last scan line of a DLI-tagged mode line. DLI routine should write hardware registers as soon as possible, preferably using WSYNC to land mid-HBLANK.

### Required DLI Boilerplate

```asm
        ; Install DLI — do this BEFORE enabling NMIEN
        lda #<my_dli_handler
        sta VDSLST
        lda #>my_dli_handler
        sta VDSLST+1

        lda #$C0            ; VBI+DLI enabled
        sta NMIEN

my_dli_handler
        pha                 ; save accumulator
        txa
        pha                 ; save X
        tya
        pha                 ; save Y

        ; --- critical register writes go here ---
        ; Use WSYNC to hit horizontal blank before writing color/P/M regs
        sta WSYNC
        lda #$0C            ; example: COLPF0 = teal
        sta COLPF0          ; $D016 — GTIA hardware register
        sta WSYNC           ; optional: land on next scan line for color change
        lda #$62
        sta COLPF1          ; $D017

        ; --- done, restore and return ---
        pla
        tay
        pla
        tax
        pla
        rti                 ; restores P register (I flag etc.)
```

**10-cycle rule:** On the very first scan line of a Mode 4 mode line (with DLI), only ~10 CPU cycles are available *before* ANTIC's playfield DMA starts. Avoid WSYNC-only colour DLI here. Use the scan line *after* the label as the DLI target, or check VSCROL>0.

### DLI timing window (OS handler vs bare-metal)

| Method | Handler entry (OS) | Handler entry (bare-metal) |
|---|---|---|
| OS via VDSLST | Cycle 28–36 | — |
| Direct vector (no OS) | — | Cycle 17 |

OS path adds 11 cycles (BIT NMIST / BPL not-taken / JMP(VDSLST)) before your handler executes; plus refresh DMA → entry at cycle 28–36 instead of cycle 17.

### Hardware vs Shadow registers — DLI gotcha

Shadow registers (page 2, e.g. `COLOR0=$2C4`) are **VBI-updated back to hardware**. Changes to shadow regs during DLI do **not** propagate to hardware until VBI. For immediate visual effect in a DLI, write to **hardware registers** `$D016` not `$2C4`.

```
Shadow → Hardware mapping during DLI:
  GPRIOR  ($022E) → PRIOR   ($D01B) must use PRIOR hardware directly
  PCOLR0  ($02C0) → COLPM0  ($D012) — use $D012
  PCOLR1  ($02C1) → COLPM1  ($D013)
  PCOLR2  ($02C2) → COLPM2  ($D014)
  PCOLR3  ($02C3) → COLPM3  ($D015)
  COLOR0  ($02C4) → COLPF0  ($D016)
  COLOR1  ($02C5) → COLPF1  ($D017)
  COLOR2  ($02C6) → COLPF2  ($D018)
  COLOR3  ($02C7) → COLPF3  ($D019)
  COLOR4  ($02C8) → COLBK   ($D01A)
  CHACT   ($02F1) → CHACTL  ($D401)
  CHBAS   ($02F4) → CHBASE  ($D409)
```

### DLI for colour-change per scan line (marching rainbow)

```asm
        ; marching rainbow: COLPF0 increments each scan line
        ; phantom DLI on blank line ($F0 instruction): DLI fires EMPTY line
rainbow_dli
        pha
        txa
        pha
        tya
        pha
        inc start_color       ; update colour in-place for next DLI
        bne ?skip
        inc start_color+1
?skip   lda start_color
        sta COLPF0            ; $D016
        ; WSYNC is not needed here — already at scan-line boundary
        ; but WSYNC ensures no mid-scanline colour-bleed
        sta WSYNC
        lda start_color+1
        sta COLPF0+1          ; or make start_color a single-byte counter
        pla
        tay
        pla
        tax
        pla
        rti
```

`start_color` updated once by VBI on DLI exit (or update directly in DLI with one-byte `INC` as shown).

---

## 3.7  WSYNC — Exact Timing

Write to `$D40A` halts the CPU until the end of the current scan line (~cycle 105 of 114). CPU resumes at cycle 104-style — the instruction *already* at cycle 105.

**Three variance sources:**

1. **Playfield DMA at cycle 105:** wide/normal + hscroll → CPU restart delayed +1  
2. **Refresh DMA at cycle 105/106:** first scan line of a character mode → further +1/+2  
3. **DMA blocked write cycle:** if *immediately-after* WSYNC is blocked → instruction starts over

Variance: up to **3 extra cycles** after WSYNC on a heavily-dma'd line. For cycle-exact DLI timing, write WSYNC twice during VBLANK to calibrate.

```asm
        ; Safe way to calibrate cycle count: do this in VBI
        sta WSYNC             ; waits to end of current scan line
        sta WSYNC             ; guarantees: we are at scan-line 0
```

**Writes to WSYNC also delay IRQ acknowledgment** — the CPU can't enter an ISR until the WSYNC delay expires. If DLIs are active, use VCOUNT polling as an alternative.

---

## 3.8  DLI Positioning — Multiple DLIs on Screen

### DLI chaining (VDSLST pointer swap)

```asm
        ; VBI sets up page-aligned DLI chain
        ; Page-aligned DLI = 6-cycle savings vs full 16-bit pointer reload

dli1    *= $2000    ; DLI subroutines must be page-aligned
        pha
        txa
        pha
        tya
        pha
        ; byte 0 corresponds to scan-line-relative DLI body
        nop
        nop

dli2    *= $2100    ; next DLI at next page

; VBI installs:
        lda #<dli1
        sta VDSLST
        lda #>dli1
        sta VDSLST+1
```

### Moving DLI positions dynamically

```asm
; Change DLI position mid-frame: modify DLI bit in the display-list byte
; dl_byte = absolute address of a display-list instruction in the scrolling region
move_dli_down
        ; scan_line → dl_byte offset lookup table
        lda scan_line
        tax
        lda dli_lookup_low,x
        sta dli_byte_pointer
        lda dli_lookup_high,x
        sta dli_byte_pointer+1

        ldy #0
        lda (dli_byte_pointer),y   ; read display list byte
        ora #$80                    ; set DLI bit
        sta (dli_byte_pointer),y
        rts
```

---

## 3.10  GTIA 9++ — Kernel DLI (Mode E Fine Vertically Scrolled)

Concept: VSCROL = 3 at *end* of mode-line (reducing height), VSCROL = 13 at start of next, forces the row-counter to loop 3→15, repeating every row → each scan line = 4 pixels tall. This creates GTIA 9++ with Mode-E pixel density but drastically reduced DMA.

```asm
        ; DLI kernel executing through all 192 line-by-line GTIA Mode E lines:
        lda #$03       ; VSCROL = 3 at end of line
        sta VSCROL
        sta WSYNC      ; end this scan line at row 3
        lda #$0D       ; VSCROL = 13 next — loops row-counter from 3→15
        sta VSCROL
        sta WSYNC
        ; … repeat per scan-line DLI
```

Caution: at scan line 95 of a 192-line Mode E kernel, the new mid-screen LMS instruction's timing interacts with the VSCROL boundary. Adjust VSCROL write interval at scan line 95 or use a `STA VSCROL` post-LMS at the boundary.

---
