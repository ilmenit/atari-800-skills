# Scrolling

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
