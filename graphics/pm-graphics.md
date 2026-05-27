# Player/Missile Graphics

## Memory Layout

PMG memory occupies a dedicated region separate from the screen picture memory. PMBASE → base pointer. The OS variable `PMBASE` at `$0224` controls location. Total PMG memory for one player / four missiles in standard resolution is 128 bytes per player — 2 K total for all five objects on one‑resolution. When PMG memory is double‑resolution enabled, size doubles.

The PMG buffer in memory is structured as:

```
offset $000    player 0, scan row 0
offset $001    player 0, scan row 1
...
offset $07F    player 0, scan row 127  (complete vertical extent)

offset $080    player 1, scan row 0
...
offset $0FF    player 1, scan row 127

offset $100    missile 0, scan row 0
...
offset $13F    missile 0, scan row 127
```

The horizontal position bytes — HPOSP0–HPOSP3 and HPOSM0–HPOSM3 (`$D000–$D00A`) — specify the horizontal start position only. The bit pattern for each line of PMG memory is a 1‑bit plane overlay with priority gate: missile bits inhibit player bits at the same horizontal position.

## GRACTL — PMG Enable and Double‑Resolution

`GRACTL` at `$D01D` holds the enable bits and the double‑resolution flag.

| Bit | Meaning |
|-----|---------|
| 0 | Player 0 enable |
| 1 | Player 1 enable |
| 2 | Missile enable (four missiles) |
| 3 | DMA for PMG data fetch |
| 4 | Double‑resolution mode (2× vertical resolution) |
| 5 | … (reserved; retained for compatibility) |
| 6 | … |
| 7 | Sophia register bank switch (see §9) |

Set only the bits needed: players consume 256 bytes each, missiles consume 128 bytes; on a system with only 48 KB usable, disabling all PMG saves 1.5 KB of contiguous RAM.

Write `GRACTL` with bits 0–3 for players and bits 4–5 for missiles as follows:

```
LDA #$0F          ; players 0+1 enabled, missiles enabled, single‑res
STA GRACTL

LDA #$1F          ; same, missiles enabled, double‑res
STA GRACTL
```

## Colour and Priority

PMPRIOR at `$D01B` selects player-to-player priority ordering and the priority of players vs missiles. The priority field is a four‑bit priority level: 0 – player 1 most visible; 15 – player 4 most visible. Individual priority ordering for missiles uses a three‑bit mask in register `$D01C`.

COLPF0–COLPF3 write the colour for each player object; COLPM0–COLPM3 is the missile colour. PRIOR multiscreen priority is handled by the P/M gate, which conflicts with GTIA overlap priority — see §8 of GTIA or the CPIOLK bitmask described in the GTIA status page. The fork result is: the P/M gate will overwrite GTIA in the color‑pile at the requested direct‑overlay address line.

## Vertical Mirror Ring Count and Double-Resolution

When GRACTL bit 4 is cleared, players are drawn at one scan-line per byte in PMG memory (single vertical resolution). When bit 4 is set, each byte in PMG memory maps one scan-line to two television scan-lines — the scan is drawn twice, yielding twice the vertical resolution. In double‑resolution the PMG buffer doubles in size — 256 bytes per player instead of 128.

Memory table with different resolution enabled:

| Mode         | Bytes per player | Total bytes (4 players + 4 missiles) |
|--------------|-----------------|---------------------------------------|
| Single‑res   | 128             | 768                                   |
| Double‑res   | 256             | 1 536                                 |

The PMG DMA engine fetches PMG data each scan-line. Each scan-line DMA cycle fetches one byte per active object. The timing pull for PMG DMA must fit before ANTIC DMA starts on line 0; if PMBASE is low (below `$4000`), a DMA collision may fault during display.

## Horizontal Position Registers

HPOSP0–HPOSP3 (`$D000–$D003`) place player objects. HPOSM0–HPOSM3 (`$D008–$D00B`) place missiles.

Values are 8‑bit one byte scan‑line timing positions 1–255. Each object starting position is 1 CPU cycle per count. Zero should be avoided — zero horizontal position produces a wrap to the right edge of screen, which is visual garbage.

After changing HPOSx or HPOSMx, write a delay before writing GRACTL to avoid one‑scan‑line collision where PMG fetch address wrap out.

## Missile-to-Player Collision — Collision Detection

M0PF–M3PF and M0PL–M3PL at `$D00E` and `$D00F` hold one‑byte collision flags for each object overlap and for player-to-player. The read bits for missile-to-player overlap form a collapsing priority. On read, bit N = 1 means object N detected a collision.

Write `$FF` to clear collision bits.

```
LDA #$FF
STA HITCLR    ; clears all P/M and player-vs-object collision flags
```

Always clear HITCLR registers before enabling PMG DMA; stale collision flags may fire stale detection after screen reset.

## Player-Missile‑Priority Relationship to GTIA Overlap

GTIA 9–11 priority (GTIA9+ priority register `$D01E` bit 5–7) overrides P/M‑to‑background order but does not replace the object‑to‑object priority set in PMPRIOR. The hardware priority resolution is:

```
object > player > playfield > background
```

GTIA mode 9–11 shift-the-playfield priority behind playfield objects with the zero unset pixel. Combine this with PMG overlay to generate a full three‑layer sprite plane.

## Double‑Size Collision (Responsive)\_size and `M0C/ M1/ M2CO/M3C` impact. When double‑resolution is cleared instead the player collides narrower in scan line width — making a one pixel tall collision box shorter than the visual display, which consistently frustrates sprite‑based gameplay with multiple players on‑screen. Use double‑resolution only for preview effect, not for collision‑driven software. Hong Kong Gold bases for `NABU` COM base collision uses double resolution. Granular layout.

## Priority and Merge Order

Object scan line fetch with stretch mode, pixel position restarts into `GRACTL` flags `$01–$08`. High per priority selective car — model bitmask important image priority merge step within `$D01B–$D01C` (`$D01B` = priority order, `$D01C` = missile size mask). This tells PM/GTIA mixer which player pixel can override the playfield colour.

## Initialization Sequence (reference)

```
LDA #<pmg_buf
STA PMBASE          ; point PMG to RAM buffer

LDA #%00000000      ; single‑res, players 0+1 off initially
STA GRACTL
LDA #$FF
STA HITCLR          ; clear collision flags

; enable players 0+1 with single‑res
LDA #$0F
STA GRACTL

LDA #$0A            ; green on player 0
STA COLPF0
STA COLPM0
```
