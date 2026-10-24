# Registers

## 3.5  ANTIC Register Quick-Reference ($D400–$D40F)

All registers are at `$D4xx`; only low 4 address bits decoded → 16 mirrored copies.

| Register | Address | R/W | Description |
|---|---|---|---|
| DMACTL | `$D400` | W | DMA control: bits 0–1 = width (0=off/1=narrow/2=normal/3=wide); bit 2=missile DMA; bit 3=player DMA; bit 4=single-line PMG; bit 5=playfield/display-list DMA |
| CHACTL | `$D401` | W | Character mode control: bits 0=blank attributed cells (software blink), 1=inversion, 2=vertical reflect |
| HSCROL | `$D404` | W | Horizontal fine scroll 0–15 |
| VSCROL | `$D405` | W | Vertical fine scroll 0–15 |
| PMBASE | `$D407` | W | High byte of P/M DMA base; 1K alignment in double-line mode, 2K in single-line mode |
| CHBASE | `$D409` | W | High byte of character-set base; 1K alignment in modes 2–5, 512-byte alignment in modes 6–7 |
| VCOUNT | `$D40B` | R | Vertical counter at two-scanline resolution; terminal readings up to 131 NTSC / 156 PAL |
| PENH | `$D40C` | R | Light pen horizontal (color clocks $22–$DD) |
| PENV | `$D40D` | R | Latched vertical position in two-scanline units, like VCOUNT |
| NMIEN | `$D40E` | W | NMI enable: bit 6=$40=VBI, bit 7=$80=DLI |
| NMIST | `$D40F` | R | NMI status: bit 7=DLI, bit 6=VBI, bit 5=RNMI |

Shadow (OS) register equivalents: SDMCTL=`$022F`, SDLSTL=`$0230/31`, VDSLST=`$0200/01`.

---

Source: [Altirra Hardware Reference Manual, 2026-01-02](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf), ANTIC register reference.
