# POKEY Audio Synthesis

## POKEY Overview

POKEY (POtentiometer and KEYboard) is the Atari 8-bit sound chip — four semiautonomous channels, each a frequency divider driving a polynomial counter. The divider value in AUDF determines pitch, the AUDC register configures volume and waveform distortion, and AUDCTL provides global channel configuration.

The circuit family offers far more to manipulate than orthodox square-wave synthesis would suggest: mixing two nearby frequency dividers generates fixed modulation sidebands; shifting into 16-bit mode recalibrates the pitch envelope of a long-form sequence; channel-3 timer gate can lock to frame counter tick count limits, yielding a precise fixed-rate timer on an otherwise shared clock domain.

The four audio channels are named AUDF1/AUDC1 through AUDF4/AUDC4 in hardware. All POKEY audio registers live in the I/O page `$D200–$D20F`. Later Atari models place a second POKEY at `$D210–$D21F` (stereo extension), detectable by the IRQ-avoidance method described in §7.

---

## Register Map

### Frequency Divider — AUDF1–4 ($D200, $D202, $D204, $D206)

Each AUDF register holds an 8-bit divide-by-N value. POKEY internally increments N by 1, so the effective divider is `AUDF + 1`.

```
f_out = f_clock / (2 × (AUDF + 1))
```

NTSC base clock is 63.921 kHz (often rounded to 64 kHz; use the precise value for musical tuning). PAL base clock is 63.337 kHz.

Each increment of AUDF lowers pitch by the same ~3-cent step at 63 kHz. A440 in 8-bit mode requires AUDF ≈ $48. The 16-bit paired mode (see §3.3) removes this ceiling entirely.

### Control Register — AUDC1–4 ($D201, $D203, $D205, $D207)

Bits 0–3 hold volume (0–15). Bit 4 selects forced-DC output — the PCM path. Bits 5–7 pick the distortion/noise polynomial.

```
+--+--+--+--+--+--+--+--+
| 7| 6| 5| 4| 3| 2| 1| 0|    AUDC
+--+--+--+--+--+--+--+--+
  \_______/  |  \______/
    poly      |   volume
    mode      |   (0-15)
              |
              forced output
              (bit4 = 1)
```

**Normal mode (bit 4 = 0):** distortion bits select the polynomial waveform. Distortion 5 and 7 skip the polynomial counter entirely — pure square wave, no noise floor. These are the modes used for musical lead lines and bass.

| Bits 5–7 | Polynomial | Sound character | Common use |
|----------|-----------|-----------------|------------|
| 000 | 5-bit + 17-bit | Complex noise | Explosion, wind |
| 001 | 5-bit only | Buzzy tone | Engine drone |
| 010 | 5-bit + 4-bit | Medium noise | Static |
| 011 | 5-bit only | Buzzy tone (variant) | — |
| 100 | 17-bit only | White noise | Hi-hat, snare |
| 101 | **None** | **Pure square wave** | Music lead/bass |
| 110 | 4-bit only | Rough percussive | Kick drum |
| 111 | **None** | **Pure square wave** | Music harmony |

Pure-tone control values range `$A0–$AF` (distortion 5) or `$E0–$EF` (distortion 7) with volume bits ORed in.

Bit 4 = 1 selects forced-DC output: the polynomial counter and frequency divider are both bypassed. The 4-bit volume value is pulsed directly onto the speaker output. Upsampling the result yields near-CD quality — this is the PCM path documented in §4. The PDM dual-channel extension that achieves 6–7 effective bits is described in §6.

### Global Control Register — AUDCTL ($D208)

| Bit | Hex | Function |
|-----|-----|----------|
| 7 | $80 | 9-bit polynomial count (default 17-bit). Only heard on noise modes; pure-tone modes ignore this bit. |
| 6 | $40 | Channel 1 runs from the CPU clock instead of the 63.921 kHz base. Used for 16-bit high-precision and PDM sub-sample rates. |
| 5 | $20 | Channel 3 runs from the CPU clock (1.789 77 MHz). Paired with bit 4 for 16-bit CH3+CH4 timing. |
| 4 | $10 | Join channels 1+2; CH1 becomes LSB, CH2 MSB. Single 16-bit divider: 65 536 steps. |
| 3 | $08 | Join channels 3+4; CH3 LSB, CH4 MSB. Independent of the CH1+CH2 pair. |
| 2 | $04 | High-pass filter: CH1 output sampled during CH3 divider ticks, gated through XOR. |
| 1 | $02 | High-pass filter: CH2 output sampled during CH4 divider ticks. |
| 0 | $01 | Downscale base clock to 15.700 kHz. Lowers every pitch by four octaves; useful for sub-bass drones. |

Bits 5 and 6 affect different channels — documentation frequently transposes them. Bit 5 = channel 3 tick source; bit 6 = channel 1 tick source.

Common AUDCTL presets:

```
$00   4-channel standard, 63.921 kHz base, 17-bit polynomial
$01   15.7 kHz base (bass)
$50   CH1+CH2 joined, CH1 at 1.789 77 MHz
$28   CH3+CH4 joined, CH3 at 1.789 77 MHz
$78   both pairs joined, both at 1.789 77 MHz
$60   CH1 + CH3 at CPU clock (for dual-channel PDM, see §6)
```

---

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

## Timer and Synch Registers

### STIMER ($D209)

Writing any value to STIMER resets all four divider counters simultaneously. Channels 1 and 2 are forced HIGH; channels 3 and 4 are forced LOW. The write is self-synchronizing — it is the only method to reset all dividers from a single write, and it is the starting point for tight PWM/PDM loops that require all channels aligned from a known state.

### IRQEN / IRQST ($D20E)

Timer interrupts fire when the channel divider reaches zero. `IRQEN` selects active IRQ sources; `IRQST` is read-only status at the same address. Clear a pending source by clearing that source's `IRQEN` bit, then set it again if the interrupt should remain enabled.

| Bit | Channel | Event |
|-----|---------|-------|
| 0 | Timer 1 | AUDF1 reached zero |
| 1 | Timer 2 | AUDF2 reached zero |
| 4 | Serial  | Data ready on SIO bus |
| 5 | Serial  | Transmit buffer empty (new byte needed) |
| 6 | Key     | Shift / Ctrl / Break key edge |
| 7 | Break   | Break key pressed |

Timer 1 is the standard interrupt clock for PCM sample playback. Timer 4 is preferred for fixed-rate ISR-driven sample streams; timing via AUDF4 interrupt delivers the cleanest sample rate with minimal jitter.

### SKCTL ($D20F) — POKEY Audio Initialization

```asm
LDA #$03   ; bits 0+1: enable keyboard scan and debounce
STA SKCTL  ; resets POKEY keyboard state; required before audio works
```

SKCTL must be written on power-up and after any SIO or cassette I/O transaction — those operations modify shared POKEY state.

---

## High-Pass Filter Operation

High-pass mode is a fully digital gate inside POKEY, not an analog RC filter. The circuit is a D flip-flop fed by the paired channel divider, with its output XORed against the current filtered-channel state.

```
filtered-channel output
        |
        v
[D  flip-flop] <--- clock = paired-channel divider ticks
        |          (current vs. previous)
        v
[XOR] <-- current output
   |
   +---- output = current XNOR previous
```

Each tick of the paired divider captures the current filtered-channel level and holds it inside the D flip-flop. The XOR compares this stored value against the live output. If the two agree, XOR returns zero; if they differ, XOR returns one.

**Behavioural table:**

| Paired divider | Input frequency | Flip-flop state | XOR output | Perceived effect |
|---------------|-----------------|----------------|------------|-----------------|
| Slower than input | Input toggles several times per D tick | Cannot track input | XOR ≅ input (rapid 0/1 toggling) | Signal passes, no attenuation |
| Equal to input | Input and flip-flop toggle in lockstep | Stored value equals input every tick | XOR = 0 (always zero) | Output near zero — series of nulls |
| Faster than input | Flip-flop toggles several times per input period | Input persists across many flip-flop transitions | XOR alternates 0/1 randomly | Output near zero — smooth null pass |

The cutoff sits approximately at the paired divider frequency (±15 % depending on phase relationship). POKEY's digital high-pass is not a smooth analog roll-off — it is a series of narrow peaks and nulls spaced at integer multiples of the filter divider. A melody line at exactly 2 kHz run through a filter clocked at exactly 2 kHz is near-zero; move the divider just 10 % and the tone opens back up.

**PDM link:** In dual-channel PDM (§6) channels 1 and 3 are set to an integer-frequency
ratio by both running from the 1.789 77 MHz clock. The XOR of the two channels produces
a fixed-order sideband train centred at exactly `|f_ch1 − f_ch3|`. This spike is the LSB
carrier. The AUDF1 and AUDF3 divider pair is selected so the spike lands at exactly
16 × the sample rate, providing exactly 16 pulse slots per sample period. The AUDF4
timer (channel 4) then runs at the same rate as channel 3, giving exactly one LSB pulse
in every 16 carrier slots:

f_sample = f_carrier / 16       (every 16th carrier slot)
        = f_cpu · |AUDF_ch1 − AUDF_ch3| / (16 · divisor_base)

The MSB nibble is held on channel 1 for the full sample period; channel 2 toggles its
4-bit LSB output at the carrier rate so each slot carries one LSB pulse. The duty-cycle
ratio for 1/16 duty: the carrier sideband lands exactly at 16×f_sample. AUDF4 runs at the carrier rate and provides the 1/16-period slot clock. AUDF2 holds the fx sample-timer value and the LSB pulse is timed exactly at the 1/16 slot edge, giving stable 1/16 duty without phase drift across periods.

```
f_sample = f_sideband / 16
        = |f_ch1 − f_ch3| / 16
        = f_cpu × |AUDF_ch1 − AUDF_ch3| / (16 × divisor)
```


---

### PCM Pre-Processing (Essential)

Before writing PCM samples to POKEY AUDC, a three-step conversion pipeline
is mandatory to avoid clipped transients, unintelligible speech, and
click/pop artefacts.  Skipping any of these steps will produce audible
quantisation floor, DC drift, or noise-floor hiss at sample-rates above 4 kHz.

| Step   | Action                               | Why                                     |
|--------|--------------------------------------|-----------------------------------------|
| **1 Normalize** | Scale input to full 0‑15 range       | Under‑used range wastes quantisation SNR |
| **2 DC Offset** | Centre values around 7‑8             | Silence emits ~$07, not $00/$0F — prevents speaker thump  |
| **3 Dither**    | Add low‑order random noise before    | Smooths quantisation banding in sibilants; converts structured |
|                 | quantisation                          | noise floor into benign random hiss     |

```asm
; Pre‑process 8‑bit sample in A → 4‑bit in A
pre_process:
    PHA                       ; save original 8‑bit
    AND #$F0                  ; high nibble → low nibble container
    LSR A ; LSR A ; LSR A ; LSR A   ; A = high nibble (0‑15)
    CLC
    ADC RANDOM                ; RANDOM ($D20A) = POKEY polynomial counter
    AND #$0F                  ; clip back to 0‑15 (dithered)
    ORA #$10                  ; forced‑output bit
    STA AUDC1
```

For dual‑channel PDM: carry the DC‑centred MSB through directly; the LSB
nibble receives only the dithered residue (no separate DC‑offset pass).


---

## AUDC Forced-DC Output — PCM Entry Point

When AUDC bit 4 = 1:

- The polynomial counter output is disconnected.
- AUDF is ignored.
- The 4-bit volume value from bits 0–3 drives the DAC directly.
- No waveform period — the output is a static level, held until the next AUDC write.

This readwrite path is how 4-bit PCM samples stream continuously on POKEY: `ORA #$10; STA AUDC1` fires a new sample value every instruction pair, at rates up to 15 kHz on NTSC systems with ANTIC DMA disabled.

Refer to `digital-audio.md` for full PCM timing methods and sample rate calculations.

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

## PAL Note Frequency Table (AUDF Values)

The following table provides pre-computed AUDF divider values for musical notes under the PAL POKEY base clock (63.337 kHz, 8-bit mode). Values are computed as `AUDF = round(63337 / (2 × f_note)) − 1`.

| Note | AUDF | Note | AUDF | Note | AUDF | Note | AUDF |
|------|------|------|------|------|------|------|------|
| H₀   | $FF  | C₂   | $78  | C₃   | $3C  | C₄   | $1D  |
| C₁   | $F1  | C♯₂  | $71  | C♯₃  | $38  | C♯₄  | $1C  |
| C♯₁  | $E3  | D₂   | $6B  | D₃   | $35  | D₄   | $1A  |
| D₁   | $D7  | D♯₂  | $65  | D♯₃  | $32  | D♯₄  | $18  |
| D♯₁  | $CB  | E₂   | $5F  | E₃   | $2F  | E₄   | $17  |
| E₁   | $BF  | F₂   | $5A  | F₃   | $2C  | F₄   | $16  |
| F₁   | $B4  | F♯₂  | $55  | F♯₃  | $2A  | F♯₄  | $14  |
| F♯₁  | $AA  | G₂   | $50  | G₃   | $27  | G₄   | $13  |
| G₁   | $A1  | G♯₂  | $4B  | G♯₃  | $25  | G♯₄  | $12  |
| G♯₁  | $98  | A₂   | $47  | A₃   | $23  | A₄   | $11  |
| A₁   | $8F  | A♯₂  | $43  | A♯₃  | $21  | A♯₄  | $10  |
| A♯₁  | $87  | H₂   | $3F  | H₃   | $1F  | H₄   | $0F  |
| H₁   | $7F  |      |      |      |      |      |      |

| Note | AUDF | Note | AUDF | Note | AUDF | Note | AUDF |
|------|------|------|------|------|------|------|------|
| C₅   | $0E  | C₆   | $07  | C₇   | $03  | C₈   | $01  |
| C♯₅  | $0D  | C♯₆  | $06  | C♯₇  | $03  | C♯₈  | $01  |
| D₅   | $0C  | D₆   | $06  | D₇   | $02  | D₈   | $01  |
| D♯₅  | $0C  | D♯₆  | $05  | D♯₇  | $02  | D♯₈  | $01  |
| E₅   | $0B  | E₆   | $05  | E₇   | $02  | E₈   | $01  |
| F₅   | $0A  | F₆   | $05  | F₇   | $02  | F₈   | $00  |
| F♯₅  | $0A  | F♯₆  | $04  | F♯₇  | $02  | F♯₈  | $00  |
| G₅   | $09  | G₆   | $04  | G₇   | $02  | G₈   | $00  |
| G♯₅  | $09  | G♯₆  | $04  | G♯₇  | $01  | G♯₈  | $00  |
| A₅   | $08  | A₆   | $03  | A₇   | $01  | A₈   | $00  |
| A♯₅  | $07  | A♯₆  | $03  | A♯₇  | $01  | A♯₈  | $00  |
| H₅   | $07  | H₆   | $03  | H₇   | $01  | H₈   | $00  |

The European notation uses H for B-natural and B for B-flat. The following B-flat aliases match the H entries above:

```asm
B_0 equ H_0    B_1 equ H_1    B_2 equ H_2    B_3 equ H_3
B_4 equ H_4    B_5 equ H_5    B_6 equ H_6    B_7 equ H_7    B_8 equ H_8
```

### Usage

Write the AUDF value to the desired POKEY audio channel register for 8-bit mode with PAL timing:

```asm
LDA #C_4          ; $1D — middle C on PAL
STA AUDF1
LDA #$A8          ; distortion 5, volume 8
STA AUDC1
```

For 16-bit paired mode (1.789 77 MHz CPU clock), compute the combined divider value instead; the 8-bit table above applies to the 63.337 kHz base clock only.

---
