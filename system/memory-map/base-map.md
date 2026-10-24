## 2.1  Full 64 K Memory Map ($0000 – $FFFF)

The Atari 8-bit has a flat 64 K 16-bit address space. Installed RAM, cartridges,
and model-specific ROM banking determine which regions are accessible.

### Map by region

| Region | Purpose |
|---|---|
| `$0000–$00FF` | Zero page — OS, user, FP (floating-point) slots |
| `$0100–$01FF` | Hardware stack — 256 bytes, grows down |
| `$0200–$02FF` | OS database, interrupt vectors, and hardware shadows (`VDSLST`, `VVBLKI`, `SDLSTL`, `CH`) |
| `$0300–$030B` | SIO Device Control Block (DCB), from `DDEVIC` to `DAUX2` |
| `$030C–$033F` | OS I/O workspace and handler table (`HATABS` at `$031A`) |
| `$0340–$03BF` | Eight IOCBs, 16 bytes each |
| `$03C0–$03FC` | Printer buffer and model-dependent OS workspace |
| `$03FD–$047F` | Cassette buffer area (`CASBUF` starts at `$03FD`) |
| `$0480–$05FF` | Application / language / floating-point workspace; includes `LBUFF` at `$0580`, not all freely available |
| `$0600–$06FF` | Page six, normally available for user code unless another resident program uses it |
| `$0700–$7FFF` | RAM for DOS, programs, display memory, and buffers as allocated; consult `MEMLO`/`MEMTOP` |
| `$8000–$9FFF` | RAM or cartridge ROM, depending on cartridge mapping |
| `$A000–$BFFF` | RAM, cartridge ROM, or built-in BASIC ROM on XL/XE when enabled |
| `$C000–$CFFF` | XL/XE OS ROM when enabled; normally unpopulated on stock 400/800 |
| `$D000–$D7FF` | Hardware I/O: GTIA `$D0xx`, PBI `$D1xx` (XL/XE), POKEY `$D2xx`, PIA `$D3xx`, ANTIC `$D4xx`; remaining pages are model/expansion dependent |
| `$D800–$DFFF` | Floating-point ROM (part of the banked OS ROM on XL/XE) |
| `$E000–$FFFF` | 8K OS ROM region; XL/XE also maps OS ROM at `$C000–$CFFF` and `$D800–$DFFF` |

RAM is only present up to the installed size. DOS, cartridges, and resident
handlers may reserve otherwise usable RAM; check ownership before using it.
Reference: [cc65 Atari definitions](https://github.com/cc65/cc65/blob/master/asminc/atari.inc), OS RAM variables and hardware equates.

### Zero page zones

| Zone | Range | Notes |
|---|---|---|
| OS workspace | `$00–$7F` | Includes timers, pointers, CIO zero-page IOCB (`$20–$2F`), and editor workspace; not generally free |
| Language / application workspace | `$80–$D3` | Availability depends on BASIC, DOS, and other resident software; reserve explicitly |
| Floating-point workspace | `$D4–$FF` | Reuse only if no active code needs the OS floating-point routines |

Joystick/paddle shadows live in page two (for example, `PADDL0 $0270` and
`STICK0 $0278`); `WSYNC` is hardware at `$D40A`, not a zero-page shadow.

### PIA 6520 (Peripheral Interface Adapter)

Address range: `$D300–$D3FF`, only bits 0–1 decoded → 4 mirrored locations:  
`$D300/$D301/$D302/$D303` / `$D304/$D305/$D306/$D307` / … / `$D3FC/$D3FD/$D3FE/$D3FF`

| Register | Address | Function |
|---|---|---|
| PORTA | `$D300` | Joystick directions ports 1/2 (read); DDRA selected when PACTL bit 2=0 |
| PORTB | `$D301` | Port data; banking/ROM enable on XL/XE (output: bits 0,1,4,6,7); joystick ports 3/4 on 400/800 |
| PACTL | `$D302` | Port A control register (data direction + interrupt enable) |
| PBCTL | `$D303` | Port B control register (same layout as PACTL) |
| DDRA | bit=write to $D300 when PACTL.bit2=0 | Data direction: 0=input, 1=output |
| DDRB | bit=write to $D301 when PBCTL.bit2=0 | Data direction: 0=input, 1=output |

**PIA control-line setup (partial snippet)**

```asm
        ; Typical PACTL/PBCTL init on XL/XE
        lda #$34             ; CA2 low, CB2 low, interrupts disabled
        sta PACTL
        sta PBCTL
```

**400/800 RESET key:** RNMI asserted on leading edge of VBLANK → OS warm-start.  
**XL/XE RESET key:** Asserts the hardware reset path and fetches the CPU reset
vector at `$FFFC/$FFFD`. The OS then decides warm versus cold start; pressing
System Reset is not automatically a cold boot.

---
