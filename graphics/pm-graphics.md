# Player/Missile Graphics

> **Scope:** Atari hardware players and missiles, PMG memory, GTIA registers, priority, size, movement, and collisions.
> **Do not use for:** CPU-rendered software sprites; use `graphics/software-sprites.md`.

## Quick-Lookup

| Need | See |
|---|---|
| PMG memory layout | §1 |
| Enable sequence | §2 |
| Move players/missiles | §3 |
| Colors, sizes, priority | §4 |
| Collision registers | §5 |
| DLI multiplexing | §6 |

## §1 PMG Memory Layout

PMG data is fetched by ANTIC DMA from the base selected by `PMBASE ($D407)`. The value written to `PMBASE` is the high byte of the PMG area.

Resolution is selected by `DMACTL`:

| Mode | DMACTL bit 4 | Alignment | Bytes per player | Notes |
|---|---:|---:|---:|---|
| Double-line | 0 | 1 KB practical minimum | 128 | One PMG byte covers two scan lines |
| Single-line | 1 | 2 KB practical minimum | 256 | One PMG byte covers one scan line |

Common offsets from the PMG base:

| Object | Double-line offset | Single-line offset |
|---|---:|---:|
| Missiles | `$0300` | `$0300` |
| Player 0 | `$0400` | `$0400` |
| Player 1 | `$0500` | `$0500` |
| Player 2 | `$0600` | `$0600` |
| Player 3 | `$0700` | `$0700` |

Single-line mode uses twice as many bytes vertically, so reserve a 2 KB aligned region even though the offsets look the same.

## §2 Enable Sequence

Two chips participate:

- `DMACTL ($D400)` enables ANTIC fetching of missile/player data.
- `GRACTL ($D01D)` enables GTIA display of fetched missile/player graphics.

Useful bits:

| Register | Bit | Meaning |
|---|---:|---|
| `DMACTL` | 2 | Missile DMA |
| `DMACTL` | 3 | Player DMA |
| `DMACTL` | 4 | Single-line PMG resolution |
| `DMACTL` | 5 | Display-list DMA |
| `GRACTL` | 0 | Missile display enable |
| `GRACTL` | 1 | Player display enable |
| `GRACTL` | 2 | Trigger latch enable |

```asm
pm_base_page = >pm_area

init_pmg
        lda   #0
        sta   GRACTL

        lda   #pm_base_page
        sta   PMBASE          ; $D407

        lda   #0
        ldx   #0
?clear  sta   pm_area,x
        sta   pm_area+$100,x
        sta   pm_area+$200,x
        sta   pm_area+$300,x
        sta   pm_area+$400,x
        sta   pm_area+$500,x
        sta   pm_area+$600,x
        sta   pm_area+$700,x
        inx
        bne   ?clear

        lda   #%00111110      ; DL DMA + single-line PMG + players + missiles + normal PF
        sta   DMACTL
        lda   #%00000011      ; show missiles + players
        sta   GRACTL
        lda   #$ff
        sta   HITCLR
        rts
```

If the OS is active, write the OS shadow `SDMCTL ($022F)` instead of only `DMACTL`; the OS VBI copies `SDMCTL` back to hardware.

## §3 Move Players and Missiles

Vertical movement is a memory copy into the object's PMG lane. Clear at least one byte above and below the previous footprint to prevent trails.

```asm
move_player0
        ; A/X = source pointer, Y = vertical byte offset, hpos = horizontal position
        sta   src
        stx   src+1
        sty   vpos

        lda   #0
        sta   pm_area+$0400-1,y
        sta   pm_area+$0400+sprite_h,y

        ldx   vpos
        ldy   #0
?copy   lda   (src),y
        sta   pm_area+$0400,x
        inx
        iny
        cpy   #sprite_h
        bne   ?copy

        lda   hpos
        sta   HPOSP0          ; $D000
        rts
```

Horizontal position registers:

| Register | Address | Object |
|---|---:|---|
| `HPOSP0`-`HPOSP3` | `$D000`-`$D003` | Players |
| `HPOSM0`-`HPOSM3` | `$D004`-`$D007` | Missiles |

## §4 Colors, Sizes, and Priority

| Register | Address | Purpose |
|---|---:|---|
| `PCOLR0`-`PCOLR3` | `$02C0`-`$02C3` | OS shadows for player/missile colors |
| `COLPM0`-`COLPM3` | `$D012`-`$D015` | Hardware colors; write in DLI |
| `SIZEP0`-`SIZEP3` | `$D008`-`$D00B` | Player horizontal size |
| `SIZEM` | `$D00C` | Two bits per missile size |
| `PRIOR` | `$D01B` | P/M vs playfield priority and fifth-player mode |

Player size values are `0` normal, `1` double width, `3` quadruple width. `SIZEM` packs four 2-bit missile sizes:

```asm
; missile 0 normal, missile 1 double, missile 2 quad, missile 3 normal
        lda   #%00110100
        sta   SIZEM
```

Use `PCOLR0`-`PCOLR3` during normal OS-driven frames. Use `COLPM0`-`COLPM3` directly inside DLI code because shadow writes will not affect the current scan line.

## §5 Collision Registers

PMG collision latches remain set until `HITCLR ($D01E)` is written.

| Range | Purpose |
|---|---|
| `$D000`-`$D003` read | Missile-to-playfield collisions |
| `$D004`-`$D007` read | Player-to-playfield collisions |
| `$D008`-`$D00B` read | Missile-to-player collisions |
| `$D00C`-`$D00F` read | Player-to-player collisions |

```asm
read_collision
        lda   P0PF            ; player 0 vs playfields
        bne   ?hit
        rts
?hit    lda   #$ff
        sta   HITCLR
        rts
```

Clear `HITCLR` after initializing PMG and after each collision sample.

## §6 DLI Multiplexing

Hardware gives four players and four missiles, but a DLI can reuse them in separate vertical bands by changing `HPOSPn`, `SIZEPn`, `COLPMn`, and the PMG memory bytes before the next band is drawn.

Rules:

- Precompute band position/color tables in VBI; keep DLI work to loads and stores.
- Page-align DLI handlers when a chain is long.
- Leave a vertical gap when reusing one player in adjacent bands, especially in Mode 4 displays where tight timing can expose a one-scan-line artifact.
- If a tracker or another subsystem owns `VDSLST`, centralize DLI ownership instead of installing competing handlers.

For CPU-rendered sprite engines that combine with PMG overlays, keep PMG for small high-priority objects and use `graphics/software-sprites.md` for the background sprite layer.
