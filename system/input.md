---
name: atari8bit-input
description: >-
  Atari 8-bit input device registers — joystick DB9 ports, STICK/TRIG/PADDL, light pen PENH/PENV, CONSOL keys, XEP80.
---

# 06 — Input Devices

> Supplementary code patterns from Atari 8-bit reference articles and hardware reference cards. Content is self-contained.
> **Scope:** Joystick/paddle/trackball, mouse/tablet, light pen, XEP80, console keys
> **Key items:** STICK0-3 OS shadows $0278-$027B, PORTA/PORTB $D300/$D301, TRIG0-3 $D010-$D013, PADDL0-7 shadows $0270-$0277 / hardware $D200-$D207, CONSOL $D01F, PENH/PENV $D40C/$D40D

## Quick-lookup

| Need | See § |
|---|---|
| DB9 pinout and model port mapping | §6.0 |
| STICK OS shadows vs PIA hardware | §6.1 |
| TRIG per-trigger read | §6.1 |
| PADDLn RC-time; wait \u2265256c | §6.1 |
| Mouse delta via PADDLn (EOR#FF+ADC trick) | §6.1 |
| Light pen (PENH/PENV valid range) | §6.2 |
| CONSOL start/select/option + clear-to-write | §6.2 |
| XEP80 / Touch tablet | §6.2 |

## 6.0 DB9 Port and Model Mapping

The 9-pin controller port uses four digital direction lines, two analog paddle inputs, one trigger, +5V, and ground:

| Pin | Signal |
|---|---|
| 1-4 | Direction bits 0-3 |
| 5 | Paddle input 1 |
| 6 | Trigger |
| 7 | +5V |
| 8 | Ground |
| 9 | Paddle input 0 |

Logical port ownership:

| Port | Digital bits | Analog channels | Trigger |
|---|---|---|---|
| Joy 0 | PORTA bits 0-3 | POT0/POT1 | TRIG0 |
| Joy 1 | PORTA bits 4-7 | POT2/POT3 | TRIG1 |
| Joy 2 | PORTB bits 0-3 | POT4/POT5 | TRIG2 |
| Joy 3 | PORTB bits 4-7 | POT6/POT7 | TRIG3 |

XL/XE machines expose two controller ports; 400/800 machines expose four. On XL/XE, PORTB is also used for OS/BASIC/self-test/extended-RAM control, so do not assume ports 2-3 exist or that PORTB can be repurposed safely.

## 6.1 Joystick, Paddle & Mouse Registers

Joystick directions are read from the PIA ports, not from the GTIA `$D000` player-position registers. For OS-friendly code, read the VBI-updated shadows; for tight polling or unusual devices, read PIA directly.

| Register | Range | Purpose |
|---|---|---|
| STICK0-STICK3 | $0278-$027B | OS joystick direction shadows, active-low low nibble |
| PORTA | $D300 | Hardware directions for joystick ports 0-1 |
| PORTB | $D301 | Hardware directions for joystick ports 2-3 on 400/800; XL/XE ROM/RAM banking control |
| TRIG0-TRIG3 | $D010-$D013 | Per-trigger read, active low |
| CONSOL         | $D01F   | Console start/select/option keys |
| PADDL0-PADDL7 | $0270-$0277 | OS paddle shadows |
| POT0-POT7 | $D200-$D207 | Hardware paddle RC-time counters |

### Register map

| Register | Address | R/W | Description |
|---|---|---|---|
| `STICK0` | `$0278` | R | OS shadow for joystick 0 |
| `STICK1` | `$0279` | R | OS shadow for joystick 1 |
| `STICK2` | `$027A` | R | OS shadow for joystick 2 on 400/800 |
| `STICK3` | `$027B` | R | OS shadow for joystick 3 on 400/800 |
| `PORTA` | `$D300` | R/W | Hardware direction bits for ports 0-1 |
| `PORTB` | `$D301` | R/W | Hardware port 2-3 on 400/800; XL/XE banking register |
| `TRIG0`-`TRIG3` | `$D010`-`$D013` | R | Trigger inputs; `0` = pressed |
| `STRIG0`-`STRIG3` | `$0284`-`$0287` | R | OS trigger shadows; `0` = pressed |
| `CONSOL` | `$D01F` | R(W) | Console keys are active low; write any value to clear the speaker latch |

**STICK0 OS-shadow idiom**

For OS-friendly gameplay, read the VBI-maintained `STICKn` shadow once per frame and cache it for game logic:

```asm
stick_snapshot
        lda   STICK0           ; OS shadow at $0278
        and   #$0f             ; isolate active-low direction bits
        cmp   last_stick
        beq   ?unchanged
        jsr   stick_changed     ; process new directions
?unchanged
         rts
```

Direction bits in STICKn, active low:

      bit0 = UP   bit1 = DOWN   bit2 = LEFT   bit3 = RIGHT
      0 = active, 1 = inactive

For direct hardware polling of joystick 0, read `PORTA` and mask the low nibble. For joystick 1, read the high nibble and shift or compare in place.

```asm
stick_map
        lda PORTA
        and #$0f        ; joystick 0 active-low direction nibble
```

### Paddle reading (POT timing)

POT is an RC-integrator. Writing `POTGO ($D20B)` discharges the capacitors and starts a new measurement; read `POT0-POT7` only after enough time has passed. In fast scan, wait at least 229 CPU cycles; in normal scan, wait roughly 229 scan lines or use the OS `PADDLn` shadows.

```asm
wait_paddle
        ldx   #40              ; ~40 × 7 NOPs ≥ ~288 cycles; safe margin
@loop   dex
        bne   @loop
        rts
```

XEP80 / Touch tablet (X-Modern): implemented via SIO device or through joystick-port analog; Atari 820/822 interface.

### Trigger table

| Trigger | Address | R/W | Bit | Clear by write |
|---|---|---|---|---|
| TRIG0 | $D010 | R | b0 | no; read only |
| TRIG1 | $D011 | R | b0 | no; read only |
| TRIG2 | $D012 | R | b0 | no; read only |
| TRIG3 | $D013 | R | b0 | no; read only |

### Mouse, Trackball, Tablet Notes

- Atari Touch Tablet uses the analog paddle inputs: X on pin 9, Y on pin 5, button on pin 1 or trigger depending on mode.
- CX-22 trackball and ST/Amiga mice use quadrature-like direction/reference lines on the digital pins. Treat them as edge/delta devices, not as absolute joystick states.
- Light gun trigger is on the trigger pin. Hardware notes describe reliable use on the fourth 400/800 port; XL/XE compatibility should be stated explicitly if required.

---

## 6.2 Light Pen

`PENH ($D40C)`: horizontal position — reads the color-clock counter but subtracts 34; valid range: `$22–$DD`.
`PENV ($D40D)`: vertical position — matches VCOUNT (0–255).
`VCOUNT` must wrap to verify.

```asm
        lda   PENH
        cmp   #$22             ; minimum horizontal
        bcc   ?error           ; underflow
        cmp   #$DD
        bcs   ?error           ; overflow
        ...                     ; accept valid PENH
```

---

*All register maps, timing constants and code snippets are self-contained in this file; PIA port details in `system/memory-map.md`.*
