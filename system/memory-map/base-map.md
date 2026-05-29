# Base Map

## 2.1  Full 64 K Memory Map ($0000 – $FFFF)

The Atari 8-bit has a flat 64 K 16-bit address space. Layout is fixed for all models except where extended RAM windowing and ROM bits apply.

### Map by region

| Region | Purpose |
|---|---|
| `$0000–$00FF` | Zero page — OS, user, FP (floating-point) slots |
| `$0100–$01FF` | Hardware stack — 256 bytes, grows down |
| `$0200–$02FF` | DOS control block (buffer pointer etc.) |
| `$0300–`..| OS screen/line edit buffer, free RAM |
| `$D000–`..| POKEY (4 mirrors) / GTIA / PIA 6520 / ANTIC / POKEY mirrors |
| `$E000–$FFFF` | OS ROM — 8 K (400/800) or 16 K (XL/XE); basic ROM at `$A000–$BFFF` |

### Zero page zones

| Zone | Range | Notes |
|---|---|---|
| OS numbered vector table | `$00–$1F` | 32 entry points |
| OS free / unnumbered | `$20–$8F` | Mostly unused on entry; safe for user programs |
| WSYNC, STICK/PADDL shadows | `$C0–`.. | Altirra hardware calls OS page 2 shadow page |
| Floating point | `$D4–`.. | FP database on entry from BASIC init |
| FP private | `$F0–`.. | |

### PIA 6520 (Peripheral Interface Adapter)

Address range: `$D300–$D3FF`, only bits 0–1 decoded → 4 mirrored locations:  
`$D300/$D301/$D302/$D303` / `$D304/$D305/$D306/$D307` / … / `$D3FC/$D3FD/$D3FE/$D3FF`

| Register | Address | Function |
|---|---|---|
| PORTA | `$D300` | Joystick directions ports 1/2 (read); data direction chg when DDRA bit2=0 |
| PORTB | `$D301` | Port data; banking/ROM enable on XL/XE (output: bits 0,1,4,6,7); joystick ports 3/4 on 400/800 |
| PACTL | `$D302` | Port A control register (data direction + interrupt enable) |
| PBCTL | `$D303` | Port B control register (same layout as PACTL) |
| DDRA | bit=write to $D300 when PACTL.bit2=0 | Data direction: 0=input, 1=output |
| DDRB | bit=write to $D301 when PBCTL.bit2=0 | Data direction: 0=input, 1=output |

**PORTA PACTL X Micro**

```asm
        ; Typical PACTL/PBCTL init on XL/XE
        lda #$34             ; CA2 low, CB2 low, interrupts disabled
        sta PACTL
        sta PBCTL
```

**400/800 RESET key:** RNMI asserted on leading edge of VBLANK → OS warm-start.  
**XL/XE RESET key:** Assert reset lines on CPU, ANTIC, FREDDIE, PIA; cold-restarts at `$FFFC`.

---
