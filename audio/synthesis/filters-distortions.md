# Filters Distortions

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
