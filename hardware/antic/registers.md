# Registers

## 3.5  ANTIC Register Quick-Reference ($D400–$D40F)

All registers are at `$D4xx`; only low 4 address bits decoded → 16 mirrored copies.

| Register | Address | R/W | Description |
|---|---|---|---|
| DMACTL | `$D400` | W | DMA control: bits 0–1 = width (0=off/1=narrow/2=normal/3=wide); bit 2=missile DMA; bit 3=player DMA; bit 4=single-line PMG; bit 5=playfield/display-list DMA |
| CHACTL | `$D401` | W | Character mode control: bits 0=blink, 1=inversion, 2=vertical reflect |
| HSCROL | `$D404` | W | Horizontal fine scroll 0–15 |
| VSCROL | `$D405` | W | Vertical fine scroll 0–15 |
| PMBASE | `$D407` | W | P/M memory base address>>2; bits 0-1 ignored |
| CHBASE | `$D409` | W | Character set base address; bits 0-2 ignored in modes 2-5 |
| VCOUNT | `$D40B` | R | Scan-line counter 0–255 (NTSC lines 0–261) |
| PENH | `$D40C` | R | Light pen horizontal (color clocks $22–$DD) |
| PENV | `$D40D` | R | Light pen vertical (scan line 0–255, typically) |
| NMIEN | `$D40E` | R/W | NMI enable: bit 6=$40=VBI, bit 7=$80=DLI |
| NMIST | `$D40F` | R | NMI status: bit 7=DLI, bit 6=VBI, bit 5=RNMI |

Shadow (OS) register equivalents: SDMCTL=`$022F`, SDLSTL=`$0230/31`, VDSLST=`$0200/01`.

---
