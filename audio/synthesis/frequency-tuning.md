# Frequency Tuning

## 16-Bit Mode

Joined-channel pairs construct a 16-bit divider from two 8-bit registers:

```
N = AUDF_LSB + (AUDF_MSB × 256)
f_out = f_clock / (2 × (N + 1))
```

A440 at the 1.789 77 MHz clock:

```
N = 1 789 770 / (2 × 440) − 1 = 2 033 = $07F1
AUDF1 (CH1, LSB) = $F1
AUDF2 (CH2, MSB) = $07
```

When channels are joined, only the first channel in each pair produces acoustic output. The second channel contributes its divider value purely as the high byte.

---

## Base Clock Reference Values

NTSC:

```
CPU clock         1.789 770 MHz
POKEY base        63.921 kHz   (CPU ÷ 28)
POKEY alt         15.700 kHz   (CPU ÷ 114)
```

PAL:

```
CPU clock         1.773 447 MHz
POKEY base        63.337 kHz
POKEY alt         15.560 kHz
```

For musical pitch it is the 1.789 77 MHz value that matters when paired with 16-bit mode. For typical 8-bit game tones the 63.921 kHz (NTSC) / 63.337 kHz (PAL) base clock is sufficient and AUDF values are portable.

---

## Dual Channel Precision Tuning

When exact pitch is needed and one divider channel is not enough, switch to a higher-precision paired-channel setup, patch the two 8-bit dividers together, and route the combined output to the shared speaker. This matches the period for the upper half of the sequence and re-aligns the frequency offset.

Whatever the computational result, this enables a tuning factor that oscillates around the target frequency with pitch error below 1 cent across the entire measured range. Handful calibration is optional; you can also pre-calculate both AUDF values rather than derive them on the fly.

---

### PDM Best Practices — Cycle-Perfect Timing

PDM tolerates no unpredictable variation in code-path length.  Every entry/exit
path through the sample ISR must take exactly the same number of cycles regardless
of which branches are taken. One cycle of extra latency on a single sample shifts
the LSB slot phase, producing audible phase-ringing/ghosting.

```asm
; ----
; Correct PDM sample ISR skeleton (cycle-counted path)
; ----
;   Load 8-bit sample:  5 cycles  (LDA indY)
;   Shift MSB nibble:   8 cycles  (4 × LSR)
;   ORA #$10:           2 cycles  (forced-output MSB)
;   STA AUDC1:          5 cycles  (output MSB)
;   AND #$0F:           2 cycles  (extract LSB nibble)
;   ORA #$10:           2 cycles  (LSB forced-output)
;   STA AUDC2:          5 cycles  (pulse LSB channel)
;   Advance pointer:    5–7 cycles (INY + BNE + TYA combined)
;   RTI:               10 cycles
;   Total:            ~44 cycles — must be identical for every branch taken
;---

; ─── Hardware state required before PDM ISR entry ───
;   STA DMACTL  $00  — disable screen DMA (ANTIC DMA steals cycles unpredictably)
;   STA NMIEN   $00  — disable NMIs (DLI/VBL cannot pre-empt the ISR)
;   SEI              — disable IRQs (timer IRQs must not fire midpattern)
; ────────────────────────────────────────────────────

; Each BCC/BCS/BNE/BEQ pair must perform exactly identical
; path extensions so that the branch-taken and branch-not-taken totals match.
```

Without all three hardware-lock steps (`STA DMACTL`; `STA NMIEN`; `SEI`) the ISR
path length is non-deterministic.  A single stolen DMA cycle shifts the LSB slot
boundary by 1/Nth of a carrier period, producing a comb-filter notch or phase-skip
that is audible as a metallic ping.  On PAL systems the DMA steal cycle depth is
roughly 8 % higher — verify PAL-specific reload values vs NTSC to compensate.

---
