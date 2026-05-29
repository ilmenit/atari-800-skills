---
name: atari8bit-digital-audio
description: >-
  Atari POKEY digital audio playback: 4-bit volume-only PCM/PDM, VCOUNT-timed
  sample kernels, nibble packing, channel selection, timing, and IRQ coexistence.
---

# 4-Bit Digital Sample Playback

POKEY volume is a 4-bit register ($0–$F for AUDCn volume bits). Rapidly writing volume-only values to AUDC3/AUDC4 produces 4-bit digital audio. Unpack a full 8-bit sample into two nibbles: upper nibble → high volume burst; lower nibble → next burst. At ~3.9 kHz (one nibble every two scan lines on NTSC), the result is a clean 4-bit sample stream.

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

> [!WARNING]
> **Sample overflow:** 4-bit packed samples use approximately 2 bytes per sample nibble (2 bytes per 3.9 kHz sample = ~7.7 KB/s). For a 6-second song at that rate → 46 KB stored in Atari memory. Use a single-player VBI-driven pre-fetched ring buffer to avoid sourcing from the wrong bank of extended RAM. Keep sample in consecutive ROM pages (e.g., $6000–$7FFF bankswitched) to avoid extra cycle from incrementing ZP pointer across pages.

> [!WARNING]
> **÷0 in VCOUNT timing:** VCOUNT is 8-bit (0–255); PAL machines reach scan line 155, NTSC machines wrap at scan line ~262 but the counter only counts to 255. Always use `CMP next_vcount_max` where `next_vcount_max = 130` for NTSC / 155 for PAL — don't assume a universal value.

## Variable Pitch and Mixing

For one-shot effects, a fixed VCOUNT cadence is enough. For music engines or
sampled effects with pitch, keep playback time fixed and advance the sample
position by a fixed-point step.

```asm
; 16.8 fixed-point sample cursor. One output tick:
; samp_pos_hi:lo.frac points into sample data, step_hi:step_frac is pitch.
advance_sample
        lda   samp_frac
        clc
        adc   step_frac
        sta   samp_frac
        lda   samp_lo
        adc   step_lo
        sta   samp_lo
        bcc   @same_page
        inc   samp_hi
@same_page
        rts
```

Use `step = 1.0` for native pitch, `2.0` for one octave up, `$0180` for 1.5x,
etc. This changes which source samples are consumed while the POKEY output rate
stays stable.

For multiple sample voices, mix into a wider accumulator before reducing to
POKEY's 4-bit volume:

- Convert nibbles to signed or centered values before summing.
- Use a volume lookup table: `scaled = sample * volume / 16` or `/64`.
- Clamp or bias the mixed result back to `0..15`, then OR with `$10` for
  volume-only mode.
- Keep the IRQ/VCOUNT output routine constant-time; do variable work in the
  main loop or a lower-priority VBI when possible.

Interpolation can improve high-pitch playback but costs cycles. On stock XL/XE,
prefer nearest-sample stepping unless the mixer has a very small voice count.

Source note: the fixed-point stepping and volume-table advice comes from the
portable digital-mixing discussion in C= Hacking issue 20; the output register
and timing rules here remain Atari POKEY-specific.
