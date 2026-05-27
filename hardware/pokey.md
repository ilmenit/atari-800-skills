---
name: atari8bit-pokey
description: >-
  Atari 8-bit POKEY — register map, timer/DLI audio, SIO serial protocol, polynomial counters, stereo POKEY, 4-bit digital sample playback (VCOUNT-sync).
---

# 05 — POKEY — Sound & I/O Chip

> **Key items:** AUDF1-4, AUDC1-4, AUDCTL $D208, STIMER $D209, RANDOM/SKRES $D20A, POTGO $D20B, IRQEN/IRQST $D20E, SKCTL/SKSTAT $D20F
> **Scope:** POKEY ($D200-$D20F, mirrored through page $D2): timers, sound, SIO serial, polynomial counters, stereo POKEY, 4-bit digital samples

---

## Quick-lookup

| Need | See § |
|---|---|
| Register map ($D200–$D20F) | §5.1 |
| Clock paths + timer-period table | §5.2 |
| Linked 16-bit AUDF1+2 / AUDF3+4 | §5.2 |
| AUDCx distortion/waveform bits 4–7 table | §5.3 |
| SIO base timing (async receive + 960 Hz disk beep) | §5.8 |
| SIO protocol ACK/NACK/COMPLETE/ERROR | §5.4 |
| RMT / TMC2 tracker ISR boilerplate | §5.5 |
| Stereo POKEY (second chip at $D210-$D21F) | §5.6 |
| Polynomial counter widths table | §5.7 |
| **4-bit digital sample playback (VCOUNT-sync, Space Harrier pattern)** | §5.9 |

---

## §5.1  Register Map ($D200–$D20F)

Only low 4 address bits are decoded, so the canonical registers at `$D200-$D20F` mirror through page `$D2`.

| Register | Address | R/W | Description |
|---|---|---|---|
| POT0/AUDF1 | `$D200` | R/W | Paddle 0 read / channel 1 frequency divisor |
| POT1/AUDC1 | `$D201` | R/W | Paddle 1 read / channel 1 control |
| POT2/AUDF2 | `$D202` | R/W | Paddle 2 read / channel 2 frequency divisor |
| POT3/AUDC2 | `$D203` | R/W | Paddle 3 read / channel 2 control |
| POT4/AUDF3 | `$D204` | R/W | Paddle 4 read / channel 3 frequency divisor |
| POT5/AUDC3 | `$D205` | R/W | Paddle 5 read / channel 3 control |
| POT6/AUDF4 | `$D206` | R/W | Paddle 6 read / channel 4 frequency divisor |
| POT7/AUDC4 | `$D207` | R/W | Paddle 7 read / channel 4 control |
| ALLPOT/AUDCTL | `$D208` | R/W | Paddle completion bits / audio control |
| KBCODE/STIMER | `$D209` | R/W | Keyboard code / reset all four audio timers |
| RANDOM/SKRES | `$D20A` | R/W | Polynomial random value / reset SKSTAT latch bits |
| POTGO | `$D20B` | W | Strobe: start new paddle scan sequence |
| SERIN/SEROUT | `$D20D` | R/W | Serial input / serial output |
| IRQST/IRQEN | `$D20E` | R/W | IRQ status / IRQ enable mask |
| SKSTAT/SKCTL | `$D20F` | R/W | Keyboard/serial status / keyboard-serial control |

---

## §5.2  Clock Paths & Timer Periods

```
AUDCTL bits:
  bit 6 = timer 1/2 clock: 0 = 64 kHz  /  1 = 15 kHz
  bit 5 = timer 3/4 clock: 0 = 64 kHz  /  1 = 15 kHz
  bit 4 = link T1→T2     : 0 = independent  1 = T2 clocked by T1
  bit 3 = link T3→T4     : 0 = independent  1 = T4 clocked by T3
  bit 2 = speaker mode   : 0 = two-tone  1 = high-pass-filter
  bit 1 = channel count  : 0 = 16-bit (T1+T2)  1 = 4-bit
  bit 0 = T1 clock source: 0 = 64 kHz  1 = 15 kHz
```

| Clock source | Period for timer (AUDF=N) | Notes |
|---|---|---|
| 1.79 MHz (USER1/3) | `N+4` cycles | Fastest — highest precision |
| 15 kHz | `(N+1) × 114`CPU cycles | ~837 Hz at N=0 |
| 64 kHz | `(N+1) × 28` CPU cycles (~1750 Hz) | Good for short musical notes |

**Linked timers:** AUDF1 + AUDF2 form a 16-bit period; T2 counts from AUDF2, then wraps up to $FF on each T1 underflow before both reset together.

---

## §5.3  Distortion / Waveform Selection (AUDCx bits 4–7)

| Bits[7:4] | Output type | Notes |
|---|---|---|
| $0 (/0000) | Poly-5 clocked poly-9/17 | Complex noise |
| $2 (/0010) | Poly-5 clocked square | Square VCO |
| $4 (/0100) | Poly-5 clocked poly-4 | Complex tone |
| $8 (/1000) | Poly-9/17 direct | 9-bit polynomial noise |
| $A (/1010) | Square wave | Cleanest 2-tone square |
| $C (/1100) | Poly-4 direct | 4-bit polynomial noise |
| Bit0     | Volume-only | All deviation bits=0 allowed; channel muted/vol-on |

---

## §5.4  SIO Serial Port

SIO bus: 1 leader byte ($55 AA55...) -> Device_ID ($40-$4F) -> COMMAND frame -> ACK/NACK -> DATA frame(s) -> STATUS frame. `SERIN` / `SEROUT` are the byte-level serial data registers.

**SIO timeouts:** 540 ms (128-bit clock × 80 bytes ≈ 535 ms). If the drive doesn't ACK within this window, abort and report — don't retry-loop forever on a dead channel.

> ⚠ **APE-Time DCB $45 payload mismatch:** The APE-Time clock utility uses `DCB $45` (write-time) as its command, but due to a hardware POKEY-SI0 clock gating quirk on the 1090+ stock POKEY revision, the DDEVIC write accepted by the 810 is the 1-byte CX= 4 byte clock buffer, not 5 bytes. On later drives (1050/9+ modifying the stub routine to account for byte counts in the DDEVIC of 4 vs 5 fixes a one-byte DCB offset. Always read-back the DCB after power-on self-test.

---

## §5.5  POKEY SIO Timers → RMT / TMC2 Trackers

```asm
; RMT / TMC2 VBI-resync via linked timer IRQ
rmt_vbi_isr
        pha
        txa
        pha
        tya
        pha
        jsr rmt_update           ; RMT engine tick + row resync
        jsr tmc2_ui_update       ; TMC2 40x39 tracker display
        jmp XITVBV               ; $E462, correct deferred VBI exit
```

TMC2 uses the VSCROL trick to display its 40 × 39 character-mode UI during gameplay. The tracker display lives at bank 2 of the TMC2 driver; CHBASE is swapped every 2 scan lines via DLI to create the 4 + 3 pixel-row characters.

---

## §5.6  Stereo POKEY

The common stereo upgrade maps the second POKEY at `$D210-$D21F`. Use the same low-nibble register layout as the primary chip:

| Primary | Stereo POKEY | Meaning |
|---|---|---|
| `$D200/$D201` | `$D210/$D211` | AUDF1/AUDC1 |
| `$D202/$D203` | `$D212/$D213` | AUDF2/AUDC2 |
| `$D204/$D205` | `$D214/$D215` | AUDF3/AUDC3 |
| `$D206/$D207` | `$D216/$D217` | AUDF4/AUDC4 |
| `$D208` | `$D218` | AUDCTL |
| `$D209` | `$D219` | STIMER |
| `$D20E/$D20F` | `$D21E/$D21F` | IRQEN/SKCTL |

Detection should be non-destructive: save `IRQEN`, `NMIEN`, and `SKCTL`, briefly prime the second chip, test for the expected timer/IRQ behavior, then restore all registers. See `system/compatibility.md` for the stereo-detection rule; do not write `$D210-$D21F` blindly in mono-safe code.

---

## §5.7  Polynomial Counters

| Generator | Polynomial | Width | Used by AUDC |
|---|---|---|---|
| Noise 1 | x4 + x3 + x2 + x1 + 1 | 4-bit | AUDC bit6=1, clocked by poly-5 |
| Noise 2 | x5 + x3 + 1 | 5-bit | AUDC bit6=0; shifts 9/17-bit noise gen |
| Noise 3 | x9 + x5 + 1 | 9-bit | AUDC bit7=0; used for RANDOM direct |
| Noise 4 | x17 + x14 + 1 | 17-bit | AUDC bit7=0, shifts 9/17-bit |

---

## §5.8  SIO Protocol — Base Timing

| SKCTL[4:6] | Input clock | Output clock | Mode |
|---|---|---|---|
| `%000` | External | External | Clock disabled / flip-flops reset |
| `%001` | Timer 4 | Timer 1 | Async/fixed |
| `%010` | Timer 4 | Timer 2 | Async/two-tone |
| `%011` | External | Internal | Rarely used |
| `%101` | Timer 4 | External | Sync receive |
| `%110` | Timer 4 | Timer 2 | Sync transmit (two-tone) |
| `%111` | Timer 4 | Timer 1 | Sync transmit (pure tone) |

For cassette: 600 baud → TIM4 = $05CC; for disk 19200 baud → TIM4 = $0028; max internal bit rate with 1.79 MHz master → 256 KHz (÷2 slip) = 128 Kbps absolute max only when both clocks are in-phase.

**Full SIO reset:**

```asm
        lda #$00
        sta SKCTL               ; $D20F — reset all clocks
        lda #$10                ; bit 4 = async receive; T3+T4 = 1.79 MHz
        sta SKCTL
        sta AUDF3               ; $D204
        lda #$28                ; 19200 baud divider
        sta AUDF4               ; $D206
```

---

## §5.9  4-Bit Digital Sample Playback

POKEY volume is a 4-bit register ($0–$F for AUDCn volume bits). Rapidly writing volume-only values to AUDC3/AUDC4 produces 4-bit digital audio. Unpack a full 8-bit sample into two nibbles: upper nibble → high volume burst; lower nibble → next burst. At ~3.9 kHz (one nibble every two scan lines on NTSC), the result is a clean 4-bit sample stream.

**Source:** Ironman Atari §Pushing POKEY, Space Harrier XE playback IRQ by Chris Hutt.

**Conversion pipeline:**

1. Convert PC audio to unsigned 8-bit mono RAW @ 3.9 kHz: `sox in.wav -t raw -r 3900 -u -b -c 1 out.raw`
2. Convert RAW to 4-bit big-endian: pair bytes, take upper nibble + lower nibble of next byte → single 4-bit-packed byte.
3. In playback: read packed byte → output high nibble then low nibble → increment pointer.

**VCOUNT-based sample-play kernel (taken from Space Harrier XE):**

```asm
; play_sample — VCOUNT-sync 4-bit sample playback on audio channel 3
; Assumes: play_channel = AUDC3 ($D205)
; sample_ptr = $80/$81 (zero page)
; dest_end   = $82/$83 (end address for stop)
; Uses VCOUNT to time each sample nibble precisely

sample_nibble   = $84        ; bit 0 = which nibble pending (toggle)
sample_ptr       = $85        ; ZP pointer lo/hi already stored elsewhere
sample_hi        = $86
dest_end_lo      = $87
dest_end_hi      = $88
next_vcount      = $89

play_sample
        lda #0
        tay
        sta sample_nibble            ; reset counter
        sta next_vcount

?wait_for_vcount_130
        lda #130                     ; NTSC: max VCOUNT value before wrap
        cmp VCOUNT
        bne ?wait_for_vcount_130     ; spin until VCOUNT=130 (selected scan-line)

?main_loop
        ; advance VCOUNT target by 2 = ~3.9 kHz
        lda next_vcount
        clc
        adc #2
        cmp next_vcount_max          ; if NTSC max = 130, PAL = 155
        bcc ?no_wrap
        sbc next_vcount_max          ; wrap: subtract max (0 or 1 on overflow)
?no_wrap
        sta next_vcount

        lda sample_nibble
        eor #1                       ; toggle 0→1→0
        sta sample_nibble
        bne ?lo_nibble               ; if toggled to 1 → output high nibble next

        ; === HIGH NIBBLE ===
?hi_nibble
        lda (sample_ptr),y          ; fetch current packed byte
        lsr a
        lsr a
        lsr a
        lsr a                       ; high nibble into low bits
        ora #$10                    ; bit 4 = volume-only mode
        tax                         ; save to X
        beq ?skip_play              ; volume 0 = silent frame (unnecessary DMA)
        bne ?store_vol

?lo_nibble
        lda (sample_ptr),y          ; fetch same byte again
        and #$0F                    ; low nibble
        ora #$10
        tax
        iny
        bne ?no_page
        inc sample_hi
?no_page
        lda sample_hi
        cmp dest_end_hi
        bne ?store_vol
        cpy dest_end_lo
        beq ?stop
?store_vol
        txa                         ; volume nibble + $10 (volume-only)
        sta AUDC3                   ; $D205 — write volume to channel 3
?skip_play
        jmp ?main_loop

?stop
        lda #$00
        sta AUDC3                   ; turn off sample playback
        rts
```

> ⚠ **Sample overflow:** 4-bit packed samples use approximately 2 bytes per sample nibble (2 bytes per 3.9 kHz sample = ~7.7 KB/s). For a 6-second song at that rate → 46 KB stored in Atari memory. Use a single-player VBI-driven pre-fetched ring buffer to avoid sourcing from the wrong bank of extended RAM. Overflow: 4-bit packed samples use approximately 2 bytes per sample nibble (2 bytes per 3.9 kHz sample = ~7.7 KB/s). For a 6-second song at that rate → 46 KB ROM stored. Use long VBI-thread if sample exceeds flat 64 KB / 128 KB bank. Keep sample in consecutive ROM pages (e.g., $6000–$7FFF bankswitched) to avoid extra cycle from incrementing ZP pointer across pages.

> ⚠ **÷0 in VCOUNT timing:** VCOUNT is 8-bit (0–255); PAL machines reach scan line 155, NTSC machines wrap at scan line ~262 but the counter only counts to 255. Always use `CMP next_vcount_max` where `next_vcount_max = 130` for NTSC / 155 for PAL — don't assume a universal value.

---

Source notes: POKEY behavior is summarized from `Altirra-hardware/extracted_chapters/chapter05.md`, `atari-documentation/POKEY/POKEY.md`, `pokey-registers.txt`, and the PCM/PDM technical guide.
