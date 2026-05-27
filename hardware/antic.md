---
name: atari8bit-antic
description: >-
  Atari 8-bit ANTIC display processor — register map, display-list encoding, DMACTL/CHACTL/HSCROL/VSCROL/DLI/WSYNC, character modes.
---

# 03 — ANTIC — Display Processor

> **Key items:** DMACTL $D400, CHACTL $D401, HSCROL $D404, VSCROL $D405, PMBASE $D407, NMIEN $D40E, NMIST $D40F
> **Scope:** ANTIC DMA, playfield widths, display-list encoding, fine/coarse scroll, character modes, DLI, WSYNC

## Quick-lookup

| Need | See § |
|---|---|
| Clock tree / scan-line timing (NTSC vs PAL) | §3.1 |
| Cycle-stealing budget table | §3.1 |
| DL instruction encoding (8-bit lookup table) | §3.2 |
| Complete playfield mode table (Modes 2\u2013F) | §3.2.1 |
| Coarse/fine HSCROL | §3.3.1 |
| Fine VSCROL | §3.3.2 |
| Page-per-line 2D scrolling via LMS | §3.3 |
| 2D scrolling + DLI width-switch | §3.3.6 |
| Character modes ANTIC 2\u20137 | §3.4 |
| ANTIC register quick-ref | §3.5 |
| DLI full reference | §3.6 |
| WSYNC exact timing | §3.7 |
| Multiple DLIs on screen | §3.8 |

## 3.1  ANTIC Architecture, DMA & Timing

### Clock tree

| item | NTSC | PAL |
|---|---|---|
| Master crystal | 14.318 18 MHz | 14.187 57 MHz |
| Machine clock (CPU) | 14.318 18 ÷ 8 = **1.789 773 MHz** | 14.187 57 ÷ 8 = **1.773 447 MHz** |
| Color clock | 3.579 545 MHz (NTSC subcarrier) | 4.433 618 MHz ÷ 2 |
| Cycles / scan line | **114** | **114** |
| Scan lines / frame | 262 (NTSC) | 312 (PAL) |
| Frame rate | 59.922 71 Hz | 49.860 74 Hz |

### Playfield widths (DMACTL bits 0–1)

| Width | Color clocks | Bytes/line (normal) | Use |
|---|---|---|---|
| Narrow | 128 ($40–$7F) | 32 | Saves DMA, more CPU cycles |
| Normal | 160 ($30–$CF) | 40 | Default GR.0 width |
| Wide | 192 ($20–$DF) | 48 | Covers overscan |

Wide playfield left-clipped to 178 actual visible (ANTIC cuts 12 color clocks; right 2 cut by HBLANK).

### Cycle-stealing budget

ANTIC DMA steals CPU cycles per scan line. **These are hard limits for DLI code.**

| Scenario | Available 6502 cycles / line |
|---|---|
| Baseline (playfield DMA + refresh) | ~97 |
| Mode E bitmap (160×192 4-color) | ~57 |
| Mode 2 first scan line | ~30 (font fetch dominates) |
| Mode 2 subsequent | ~60 |
| Mode 4 + scroll + PMG | <10 first line, ~50 subsequent |

Wide playfield (+16 bytes/line) + horizontal scroll (+8 bytes/line) = **more DMA steal → fewer DLI cycles**.

### Memory refresh

ANTIC performs up to 9 refresh cycles per scan line (all 9 during VBLANK). Refresh rows are 128-entry (older ANTIC) or 256-entry (later). Any CPU or ANTIC non-refresh access to a DRAM row also refreshes that row — a DRAM access counts as a refresh in addition to doing useful work.

### Bus and video timing landmarks

For cycle-exact kernels, remember these stable hardware landmarks:

| Event | Position |
|---|---|
| Scan line length | 114 CPU cycles = 228 color clocks |
| Color clocks per CPU cycle | 2 |
| HBLANK end / wide playfield start | color clock 32 |
| Visible normal playfield start | color clock 48 |
| Narrow playfield starts | color clock 64 |
| Center of scan line | color clock 128 |
| Normal playfield end / `WSYNC` release | color clock 208 |
| HBLANK start / VCOUNT increment | color clock 222 |

Display-list bytes are fetched by ANTIC on the CPU bus; each byte costs one CPU cycle. A display-list instruction with LMS or JVB consumes the opcode plus two address bytes. Player DMA costs cycles every scan line when enabled; missile DMA is automatically enabled with player DMA.

---

## 3.2  Display List Instructions (Bitmask Encoding)

DL is a stream of 1-byte or 3-byte instructions; pointer held in `DLISTL/DLISTH` at `$230/$231`. The instruction register (ANTIC internal) is loaded each scan line.

### Instruction byte format

```
D7 D6 D5 D4 D3 D2 D1 D0
DL LMS VSC HSC MODE3..0
```

| Bit | Name | Set → |
|---|---|---|
| 7 | DLI | Fire DLI on last scan line of this instruction |
| 6 | LMS | Load Memory Scan counter (requires 2 extra address bytes, LSB first) |
| 5 | VSCROLL | Enable vertical fine-scroll for this mode line |
| 4 | HSCROLL | Enable horizontal fine-scroll for this mode line |
| 3–0 | MODE | `$0`=blank, `$1`=JVB, `$2–$F`=ANTIC modes 2–15 |
### Display-list instruction byte — complete encoding (8-bit)

Each DL instruction is read into the internal Instruction Register (IR) and executed
at the start of the mode line. LMS and JVB instructions span 2 extra bytes (LSB first).

```
    D7  D6  D5  D4  D3  D2  D1  D0
    ┌───┬───┬───┬───┬───┬───┬───┬───┐
    │DL │LMS│VSC│HSC│ IR mode (0-3)  │
    └───┴───┴───┴───┴───┴───┴───┴───┘
```

| Byte value | IR mode | DL | LMS | VSC | HSC | Extended bytes | Description |
|---|---|---|---|---|---|---|---|
| `$0x` | 0 (blank) | n/a | 0 | 0 | 0 | 0 | Blank mode line (x=blank scan count 0–15) |
| `$4x` | 0 (blank) | 0 | 1 | 0 | 0 | 2 | Blank + LMS (load memory scan address) |
| `$1x` | 1 (JVB/JMP) | n/a | x | x | x | 2 | Jump to new DL address; `$41` also suspends DMA |
| `$2x` | 2 | 0 | 0 | 0 | 0 | 0 | Mode line mode 2 (40-col, 1 KB, 2 colors) |
| `$3x` | 3 | 0 | 0 | 0 | 0 | 0 | Mode line mode 3 (40-col, 1 KB, 2 colors, 10-line) |
| `$4x` | 4 | 0 | 1 | 1 | 0 | 2 | Mode 4 + vertical-scroll + LMS |
| `$5x` | 5 | 0 | 1 | 0 | 0 | 2 | Mode 5 + LMS |
| `$6x` | 6 | 0 | 0 | 0 | 0 | 0 | Mode 6 (20-col, 512 B, 5 colors) |
| `$7x` | 7 | 0 | 1 | 0 | 0 | 2 | Mode 7 + LMS |
| `$8x` | 8 | 0 | 0 | 0 | 0 | 0 | Mode 8 (40 px, 4 colors, 4×8) |
| `$9x` | 9 | 0 | 0 | 0 | 0 | 0 | Mode 9 (80 px, 2 colors, 2×4) |
| `$Ax` | A | 0 | 0 | 0 | 0 | 0 | Mode A (80 px, 4 colors, 2×4) |
| `$Bx` | B | 0 | 0 | 0 | 0 | 0 | Mode B (160 px, 2 colors, 1×2) |
| `$Cx` | C | 0 | 0 | 0 | 0 | 0 | Mode C (160 px, 2 colors, 1×1) |
| `$Dx` | D | 0 | 0 | 0 | 0 | 0 | Mode D (160 px, 4 colors, 1×2) |
| `$Ex` | E | 0 | 0 | 0 | 0 | 0 | Mode E (160 px, 4 colors, 1×1) |
| `$Fx` | F | 0 | 0 | 0 | 0 | 0 | Mode F (320 px, 2 colors hires, 1×1) |

**Blank mode lines — IR mode 0:** Bits 4–6 encode a scan-line repeat count 1–8;
`$00`–`$07` = 1–8 blank lines with DLI permitted if bit 7 set.

**JVB — IR mode 1 + bit 6 set (`$41`):** Suspends display-list DMA until vertical blank;
re-executes every scan line 8–248 of the *next* frame. DLI bit 7 set on JVB = 241 DLIs/frame
(stack depth ~25 — never stack DLIs beyond that depth).

**LMS (Load Memory Scan) — IR mode 2–F + bit 6 set:** Two extra bytes (LSB first) write to
the memory scan counter for the next scan line. Used for page-per-line scrolling or to cross
4K playfield boundaries. Minimum one LMS at top of every display list to initialize playfield address.

**Display list cannot cross 1K boundary.** DLISTL/DLISTH wrap within 1K unless the current
instruction is JVB, in which case new values are loaded from the two address bytes.

### Instruction summary

| IR | Type | Extra bytes | Notes |
|---|---|---|---|
| `$x0` | Blank line | 0 | high nibble = blank scan line count (1–8) |
| `$x1` | Jump | 2 addr | loads `DLISTL/ DLISTH`; `$41`=JVB (wait-for-VBI, re-executed) |
| `$x2–$xF` | Mode line | 0 (or +2 if LMS) | `$44`=Mode4+LMS, `$74`=Mode4+VSC+HSC+LMS |

JL command `$x1` followed by LMS bit 6 (`$41`/`$46`) = "Jump and Wait for Vertical Blank"; display list DMA is suspended and re-execution occurs at cycle 0 of scan line 8 of the *next* frame. **DLI on JVB = DLI every scan line 8–248 (241 possible DLIs), stack depth limited to ~25.**

### Playfield modes at a glance

| IR | OS Mode | Colors | Resolution | Pixels/line (normal) |
|---|---|---|---|---|
| 2 | 0 | 2 (BAK/PF2) | 40×24 chars | 320 |
| 4 | n/a | 4+1 (BAK, PF0–2, optional PF3) | 40×24 chars | 160 |
| 5 | 1 | 4+1 | 20×12 chars | 80 |
| 6 | 2 | 5 (BAK + PF0–3) | 20×24 chars | 160 |
| 7 | 3 | 5 | 10×12 chars | 80 |
| 8–F | 8–15 | 2–4 hires fill | 40–320 dots | 40–320 |

---

## 3.3  Scrolling — Coarse & Fine (2D, Hardware-Accelerated)

### 3.3.1 Vertical coarse scrolling

Set VSCROLL bit on all lines in scrolling region; update the **first LMS address** of the scrolling region by multiples of the bytes/line (Mode 4 = 40 bytes).

```asm
; Scroll viewport DOWN one line (new data at bottom)
        lda dlist_lms+1       ; high byte of LMS address
        clc
        adc #0
        sta dlist_lms+1

        lda dlist_lms          ; low byte
        adc #40                ; +40 bytes = one Mode 4 line
        sta dlist_lms

; Timing gate: wait for VBI (RTCLOK+2 changes once per frame)
wait_vbi
        lda RTCLOK+2
?wait   cmp RTCLOK+2
        beq ?wait
```

**Scroll direction vs memory direction:**

| Action | User sees | Address move |
|---|---|---|
| Scroll **down** (content rises) | new bottom line | add bytes to LMS address |
| Scroll **up** (content falls) | new top line | subtract bytes from LMS address |

### 3.3.2 Vertical fine scrolling (VSCROL)

VSCROL (`$D405`) tells ANTIC which scan line to start rendering the first scrolled mode line. Combined with fine counts (0–15) within a character cell:

```asm
; Fine scroll unit: scan lines within one character cell
vert_scroll      = $90      ; VSCROL shadow we maintain
vert_scroll_max  = 8         ; Mode 4 has 8 scan lines per char

; Each VBI: try increment VSCROL; if wraps, do coarse scroll + reset VSCROL to 0
fine_scroll_down
        inc vert_scroll
        lda vert_scroll
        cmp #vert_scroll_max
        bcc ?done                ; still within current cell
        jsr coarse_scroll_down   ; ran out of scan lines — bump to next row
        lda #0
        sta vert_scroll
?done   sta VSCROL               ; write hardware register
        rts
```

**VSCROL deadline rules** (from the the reference manual §4.7):

| Deadline | Effect if missed |
|---|---|
| Cycle 0 of scan line | Won't affect the starting-row counter of the scrolled region |
| Cycle 108 | Won't affect the *ending* row counter of the *previous* scrolled region |
| Cycle 5 | Won't affect whether the DLI fires on this scan line |

### 3.3.3 Horizontal coarse scrolling

Every LMS address in the scrolling region must be decremented (scroll left) or incremented (scroll right) by the bytes-per-line.

*One page-per-line memory layout* (256 bytes/line, so low byte of each LMS encodes horizontal offset, high byte encodes vertical page):

```asm
; Scroll all 22 LMS addresses one byte LEFT
; dlist_lms starts at scan-line-address byte offset 4 from the display list start
coarse_scroll_left
        ldy #22              ; 22 lines in scrolling region
        ldx #4
?loop   dec dlist_lms_mode4,x   ; modify low byte of each LMS address
        inx
        inx
        inx                  ; skip 3 bytes to next LMS low-byte
        dey
        bne ?loop
        rts
```

### 3.3.4 Horizontal fine scrolling (HSCROL)

HSCROL (`$D404`) shifts the visible playfield right by 0–15 color clocks. To add fine scrolling, combine it with coarse scrolling: your VBI runs `coarse_scroll_left` when `horz_scroll` wraps from `horz_scroll_max−1` back to 0.

```asm
horz_scroll      = $91     ; HSCROL shadow
horz_scroll_max  = 4       ; Mode 4: 4 color clocks per character

fine_scroll_left
        inc horz_scroll
        lda horz_scroll
        cmp #horz_scroll_max
        bcc ?done
        jsr coarse_scroll_left
        lda #0
        sta horz_scroll
?done   sta HSCROL              ; $D404
        rts
```

**HSCROL rules:**

| Rule | Explanation |
|---|---|
| Narrow → normal → wide expansion | ANTIC reads the next-bigger width for the scrolling buffer; normal playfield automatically has a 4-byte left/right buffer |
| Wide playfield limits | No fetch expansion; must set DMACTL wide explicitly |
| GTIA 9/10/11 | HSCROL must be **even** or GTIA pairs wrong color-clock bytes into 4-bit pixels |
| Changing HSCROL mid-line | LSB affects immediately; bits 1–3 change DMA start/stop; crossing mode-line boundary can corrupt playfield DMA |

### 3.3.5 Combined 2D scrolling (complete joystick-driven example)

See §3.3.6 for the fine-scroll / 2D-scroll code pattern. Summary: VBI pre-reads joystick (STICK0 via shadow), updates HSCROL/VSCROL per 8-direction, calls coarse-left/right/up/down subroutines on wraparound. DLI on last scrolling line switches DMACTL back to normal-width before status lines.

**Direction convention:** `horz_dir = $01` for right / `$FF` for left; `vert_dir = $01` for down / `$FF` for up.  
**Diagonal correction:** each direction selects +1 coordinate each VBI; to keep visual 45°, double the VSCROL rate vs HSCROL rate (select key toggle in demo).

---

## 3.4  Character Modes (ANTIC 2–7)

| Mode | Scan lines | Characters/line | Character memory | Colors |
|---|---|---|---|---|
| 2 | 8 | 40 | 1 KB @ 1K boundary | 2 |
| 3 | 10 | 40 | 1 KB | 2 (descenders) |
| 4 | 8 | 40 | 1 KB | 4+1 |
| 5 | 16 | 40 | 1 KB | 4+1 |
| 6 | 8 | 20 | 512 B @ 512B boundary | 5 |
| 7 | 16 | 20 | 512 B | 5 |
### 3.2.1  Complete ANTIC Mode Table (Modes 2–F)

| Mode | Lines/cell | Chars/line | Memory | Align | Colors | Pixel size |
|---|---|---|---|---|---|---|
| 2 | 8 | 40 | 1 KB | 1 KB | 2 | 8×8 bit |
| 3 | 10 | 40 | 1 KB | 1 KB | 2 | 8×8 (descenders) |
| 4 | 8 | 40 | 1 KB | 1 KB | 4+1 | 4×8 |
| 5 | 16 | 40 | 1 KB | 1 KB | 4+1 | 4×8 (double height) |
| 6 | 8 | 20 | 512 B | 512 B | 5 | 8×8 (1-color-clock) |
| 7 | 16 | 20 | 512 B | 512 B | 5 | 8×8 (double height) |
| 8 | 4 | 40 | 2 KB | 2 KB | 4 | 4×4 |
| 9 | 4 | 80 | 2 KB | 2 KB | 2 | 2×4 |
| A | 4 | 80 | 2 KB | 2 KB | 4 | 2×4 |
| B | 2 | 160 | 4 KB | 4 KB | 2 | 1×2 |
| C | 1 | 160 | 4 KB | 4 KB | 2 | 1×1 |
| D | 2 | 160 | 4 KB | 4 KB | 4 | 1×2 |
| E | 1 | 160 | 4 KB | 4 KB | 4 | 1×1 |
| F | 1 | 320 | 8 KB | — | 2 hires | 1×1 (PF2 luminance) |

Key: **Lines/cell** = scan lines per character row. **Aligned** = address must be 512B/1K-aligned for char modes; bitmap modes require every-row LMS (`$40`+LMS on every scan-line instruction) for playfield widths >4K. `+1` color in modes 4/5 = background color. Mode F background = PF2 colour. Hardware P/M graphics are available over standard playfield modes when `DMACTL` missile/player DMA and `GRACTL` display bits are enabled; PMG DMA steals cycles but does not change the playfield mode.

**Dynamic CHBASE switching:** write to `CHBASE = $D409`; takes effect two cycles after write. For Mode 6/7, use CHBASE bits 0 used as mode-selection: CHBASE bit 1 must match the mode's alignment boundary for correct color-clock pipeline.

**Blink/inversion:** CHACTL bits 0–1. Bit 1 = invert cells where char-name bit 7=1; bit 0 = blank cells where char-name bit 7=1; both = inverted space.

```asm
        lda #$00            ; no blink, no invert
        sta CHACTL
        lda #$02            ; invert bit 7 characters
        sta CHACTL
```

**Vertical reflection:** CHACTL bit 2 = flip character upside-down (row 7 displayed first). Affects all modes.

---

## 3.5  ANTIC Register Quick-Reference ($D400–$D40F)

All registers are at `$D4xx`; only low 4 address bits decoded → 16 mirrored copies.

| Register | Address | R/W | Description |
|---|---|---|---|
| DMACTL | `$D400` | W | DMA control: bits 0–1 = width (0=off/1=narrow/2=normal/3=wide); bit 2=missile DMA; bit 3=player DMA; bit 4=single-line PMG; bit 5=playfield/display-list DMA |
| CHACTL | `$D401` | W | Character mode control: bits 0=blink, 1=inversion, 2=vertical reflect |
| HSCROL | `$D404` | W | Horizontal fine scroll 0–15 |
| VSCROL | `$D405` | W | Vertical fine scroll 0–15 |
| PMBASE | `$D407` | W | P/M memory base address>>2; bits 0-1 ignored |
| CHBASE | `$D409` | W | Character set base address; bits 0-2 ignored in modes 2-5 |
| VCOUNT | `$D40B` | R | Scan-line counter 0–255 (NTSC lines 0–261) |
| PENH | `$D40C` | R | Light pen horizontal (color clocks $22–$DD) |
| PENV | `$D40D` | R | Light pen vertical (scan line 0–255, typically) |
| NMIEN | `$D40E` | R/W | NMI enable: bit 6=$40=VBI, bit 7=$80=DLI |
| NMIST | `$D40F` | R | NMI status: bit 7=DLI, bit 6=VBI, bit 5=RNMI |

Shadow (OS) register equivalents: SDMCTL=`$022F`, SDLSTL=`$0230/31`, VDSLST=`$0200/01`.

---

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

## 3.9  Scrolling — DLI Parallax

**Multiple scroll regions with DLI:** each DLI changes the horizontal and/or vertical scroll register for the *next* section of the screen.

```asm
        ; VBI: set initial HSCROL/VSCROL for bands 0..11
        ; DLI band_i: reads band_dli_index LUT → HPOSPn/SIZEPn changes per band
        ;    (P/M in §3.6 fig4.2/4.3)

; Mode 4 timing note: Player 3 lags 1 scan line vs Players 0–2
; → add 6+ scan-line buffer zone; drop WSYNC from non-color DLI code
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
