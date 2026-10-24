---
name: atari8bit-input
description: >-
  Atari 8-bit input device registers — joystick DB9 ports, STICK/TRIG/PADDL, light pen PENH/PENV, CONSOL keys, XEP80.
---

# 06 — Input Devices

> Supplementary code patterns for keyboard, joystick, paddle, mouse, light-pen, and console-key input. Content is self-contained.
> **Scope:** Joystick/paddle/trackball, mouse/tablet, light pen, XEP80, console keys
> **Key items:** STICK0-3 OS shadows $0278-$027B, PORTA/PORTB $D300/$D301, TRIG0-3 $D010-$D013, PADDL0-7 shadows $0270-$0277 / hardware $D200-$D207, CONSOL $D01F, PENH/PENV $D40C/$D40D

## Quick-lookup

| Need | See § |
|---|---|
| DB9 pinout and model port mapping | §6.0 |
| STICK OS shadows vs PIA hardware | §6.1 |
| TRIG per-trigger read | §6.1 |
| ROR joystick bit-field decoder | §6.1 |
| PADDLn RC-time; wait \u2265256c | §6.1 |
| Mouse delta via PADDLn (EOR#FF+ADC trick) | §6.1 |
| Quadrature mouse nibble decoder | §6.1 |
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

### ROR joystick bit-field decoder

`STICK0` (`$0278`) is an active-low bit field, not a Gray code. A cleared bit means the direction is pressed:

```
bit 0 = UP     bit 1 = DOWN
bit 2 = LEFT   bit 3 = RIGHT
```

Using `ROR A` moves each direction bit into Carry, so a compact decoder can consume the four directions in order:

```asm
record_joystick
        lda   STICK0          ; $0278 OS shadow
        and   #$0f
        cmp   #$0f            ; centered: all direction bits high
        beq   ?none
        sta   latest_joystick
?none   lda   STRIG0          ; $0284 OS trigger shadow, 0 = pressed
        bne   ?done
        lda   #1
        sta   fire_pressed
?done   rts

process_joystick
        lda   #0
        sta   joystick_x
        sta   joystick_y

        lda   latest_joystick
        ror   a               ; bit 0 -> Carry
        bcs   ?up_clear
        dec   joystick_y
?up_clear
        ror   a               ; bit 1 -> Carry
        bcs   ?down_clear
        inc   joystick_y
?down_clear
        ror   a               ; bit 2 -> Carry
        bcs   ?left_clear
        dec   joystick_x
?left_clear
        ror   a               ; bit 3 -> Carry
        bcs   ?right_clear
        inc   joystick_x
?right_clear
        lda   #0
        sta   latest_joystick
        rts
```

For two-button joystick adapters that encode a second fire button through paddle timing, sample at the start of VBI: read `POT0`/`ALLPOT`, then write `POTGO` only after the read because `POTGO` resets the POT counters.

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

For ST/Amiga-style mouse readers, poll the joystick-port direction nibble and table-decode signed deltas. VBI-rate polling is usable for UI cursors; fast game movement should use a POKEY timer IRQ around 1 kHz and accumulate deltas for the frame.

```asm
vbi_mouse
        pha
        txa
        pha
        tya
        pha

        lda   PORTA           ; $D300, joystick-port direction lines
        pha

        and   #$0f
        tay
        lda   xtable,y
        clc
        adc   mouse_x_lo
        sta   mouse_x_lo
        lda   mouse_x_hi
        adc   #0
        sta   mouse_x_hi

        pla
        lsr   a
        lsr   a
        lsr   a
        lsr   a
        tay
        lda   ytable,y
        clc
        adc   mouse_y_lo
        sta   mouse_y_lo
        lda   mouse_y_hi
        adc   #0
        sta   mouse_y_hi

        pla
        tay
        pla
        tax
        pla
        rts
```

Amiga-compatible delta tables:

```asm
xtable  .byte  0, -1,  1,  0,  1,  0,  0, -1
        .byte -1,  0,  0,  1,  0,  1, -1,  0
ytable  .byte  0,  1, -1,  0,  1,  0,  0, -1
        .byte -1,  0,  0,  1,  0, -1,  1,  0
```

ST-compatible delta tables:

```asm
xtable  .byte  0,  1,  0, -1,  0, -1,  1,  0
        .byte  0,  1, -1,  0,  1,  0,  0, -1
ytable  .byte  0,  0, -1,  1,  0,  1, -1,  0
        .byte  0, -1,  1,  0, -1,  0,  0,  1
```

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

## 6.3 Keyboard Input

Atari 8-bit computers read keyboard input through three primary paradigms: OS Shadow registers (polling-friendly), standard OS CIO calls (via the `K:` handler), or direct hardware scanning of POKEY registers (for games and bare-metal environments).

### 6.3.1 OS Shadow Register Polling
The OS keyboard IRQ handler places accepted keypresses in the page-two `CH` shadow.

* **`CH ($02FC)`** (764): Pending keyboard scan code, including Shift/Control bits, or `$FF` if no key is pending. This is not ATASCII; CIO `GET` through `K:` performs the character translation.
  > [!IMPORTANT]
  > Once a keypress is read from `CH`, you **MUST** reset it by writing `$FF` to `CH` so the OS knows the key has been processed.
* **`SHFLOK ($02BE)`** (702): OS character-entry lock mode: `$00` = lowercase, `$40` = uppercase/Shift lock, `$80` = Control lock. This is not a live modifier-key status register.
* **`CRSINH ($02F0)`** (752): Cursor-inhibit flag (`$00` = cursor enabled). It is unrelated to keyboard modifiers; there is no `SHFLG` register here.

**Polling OS Shadow Example (OS keyboard IRQ processing must be running):**
```asm
poll_keyboard
        lda CH                 ; OS keyboard shadow at $02FC
        cmp #$FF               ; $FF = no keypress
        beq ?no_key
        
        pha                    ; save key code
        lda #$FF
        sta CH                 ; reset shadow code to acknowledge read
        pla                    ; restore key code
        
        ; ... process key in accumulator ...
?no_key rts
```

### 6.3.2 Direct Hardware Scanning (Bypassing OS)
For custom keyboard matrix decoding or when the OS ROM is disabled, POKEY registers are polled directly:

* **`KBCODE ($D209)`**: Holds the raw 8-bit keyboard matrix code.
  - Bits 0–5: Base raw scancode (0–63).
  - Bit 6: Shift modifier status (`1` = Shift is down / value + `$40`).
  - Bit 7: Control modifier status (`1` = Control is down / value + `$80`).
  - Modifier bits are latched with the key code, not updated continuously.
  - The last code remains latched after release; `$FF` is not a hardware no-key sentinel (it can encode Shift+Control+A).
* **`SKSTAT ($D20F)`**: Status register.
  - Bit 2: Non-modifier key currently pressed (`0` = key is down).
  - Bit 3: Live Shift status (`0` = Shift is down).
  - Bit 6: Keyboard overrun (`0` = a new key was detected while the previous keyboard IRQ was still pending). Reading `KBCODE` does not acknowledge the IRQ or clear overrun; writing `SKREST ($D20A)` clears the overrun flag.
* **`SKCTL ($D20F)`**: Control register (Write-only).
  - Bit 1 enables keyboard scanning; bit 0 enables debounce. Writing `$03` enables both and exits POKEY initialization mode. Do this when taking ownership of POKEY; it also changes serial-port control settings.

**Direct Hardware Reading Example:**
```asm
init_keyboard_hardware
        lda #$03
        sta SKCTL              ; enable keyboard scan and debounce logic
        rts

poll_key_hardware
        lda SKSTAT             ; read POKEY status
        and #$04               ; bit 2 = non-modifier key down, active low
        bne ?no_keypress
        
        lda KBCODE             ; read raw scancode
        cmp KBCODE             ; compare to ensure stability
        bne poll_key_hardware   ; retry if the latched code changed
        
        ; A now holds raw 8-bit scancode (including shift/ctrl bits)
        sec                    ; carry set = key held (even if code is $FF)
        rts
?no_keypress
        clc                    ; carry clear = no key; A is undefined
        rts
```

This routine reports a held key on every call. For one event per press, track
the transition from released to pressed or handle the keyboard IRQ. POKEY's
scanner supplies hardware debounce; two matching reads alone are not debounce.

### 6.3.3 Keyboard Scancodes Mapping Table
The base raw scancodes (bits 0–5 of `KBCODE`, unshifted/uncontrolled) map to standard keyboard keys as follows:

| Code | Key | Code | Key | Code | Key | Code | Key |
|---|---|---|---|---|---|---|---|
| `$00` | L | `$10` | V | `$20` | , | `$30` | 9 |
| `$01` | J | `$11` | HELP | `$21` | SPACE | `$31` | Unused |
| `$02` | ; | `$12` | C | `$22` | . | `$32` | 0 |
| `$03` | F1 (1200XL) | `$13` | F3 (1200XL) | `$23` | N | `$33` | 7 |
| `$04` | F2 (1200XL) | `$14` | F4 (1200XL) | `$24` | Unused | `$34` | BACKSPACE |
| `$05` | K | `$15` | B | `$25` | M | `$35` | 8 |
| `$06` | + | `$16` | X | `$26` | / | `$36` | < |
| `$07` | * | `$17` | Z | `$27` | INVERSE | `$37` | > |
| `$08` | O | `$18` | 4 | `$28` | R | `$38` | F |
| `$09` | Unused | `$19` | Unused | `$29` | Unused | `$39` | H |
| `$0A` | P | `$1A` | 3 | `$2A` | E | `$3A` | D |
| `$0B` | U | `$1B` | 6 | `$2B` | Y | `$3B` | Unused |
| `$0C` | RETURN | `$1C` | ESCAPE | `$2C` | TAB | `$3C` | CAPS |
| `$0D` | I | `$1D` | 5 | `$2D` | T | `$3D` | G |
| `$0E` | - | `$1E` | 2 | `$2E` | W | `$3E` | S |
| `$0F` | = | `$1F` | 1 | `$2F` | Q | `$3F` | A |

F1–F4 are physical keys only on the 1200XL; HELP is absent on the 400/800.
The six unused matrix positions have no normal key. Shift and Control are
modifiers, BREAK uses its own IRQ, START/SELECT/OPTION use `CONSOL`, and RESET
uses the system reset path. They are not additional base scan codes.

References: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), §5.8 and §14.4 (KBCODE/SKSTAT/SKCTL);
[cc65 Atari definitions](https://github.com/cc65/cc65/blob/master/asminc/atari.inc), keyboard codes and OS variables.

---

*All register maps, timing constants and code snippets are self-contained in this file; PIA port details in `system/memory-map.md`.*
