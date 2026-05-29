---
name: atari8bit-vbxe
description: >-
  VBXE — FPGA-based GTIA replacement for Atari 8-bit: FX/GTIA_emu register map, blitter, sprites, XDL, MEMAC windows, polygon/video examples.
---

# 15 — VBXE — Video Board XE (Exotic Hardware)

> **When to load:** The task requires VBXE detection, FX registers, XDL setup, VRAM access, blitter use, palette work, or VBXE example triage.
> **Scope:** VBXE: FX/GTIA_emu register map ($D6xx/$D7xx), MEMAC windows, blitter, sprites, XDL, polygon/video examples
> **Key items:** $D600/$D700 block; CORE_VERSION $D640/$D740; MEMAC B_CTL $D61D; XDL pointer; VGABLIT
> **Primary sources:** `atari-documentation/vbxe/fx1.26-en.pdf`, `Atariki/articles/rejestry_vbxe.md`, `wykrycie_vbxe.md`, `video_board_xe.md`, `atari-documentation/vbxe/Examples/FX/`

## Quick-lookup

| Need | See § |
|---|---|
| VBXE in one paragraph | §15.1 |
| FX core spec table (512KB VRAM, 21-bit palette) | §15.2 |
| Register layout table | §15.3 |
| FX CORE_VERSION $D640 / CORE_REVISION $D641 | §15.4 |
| FX detection (KMK/DLT 2009, MEMAC B_CTL trick, 36b) | §15.4 |
| XDL and minimal init | §15.5 |
| VRAM / MEMAC / blitter | §15.6 |
| EN code-examples index | §15.7 |

## 15.1 What Is VBXE

VBXE (Video Board XE) is an FPGA-based internal add-on designed by T. Piorek that replaces the GTIA on Atari 8-bit XL/XE machines. The FPGA core can be upgraded in software; the corpus includes FX 1.26 documentation. Altirra emulates VBXE as an optional device.

VBXE operates in parallel with ANTIC and GTIA: it shadows ANTIC/GTIA writes for standard display compatibility while adding an extended display list (XDL), overlay planes, an attribute map, and a hardware blitter. GTIA collision behavior remains tied to the standard ANTIC/GTIA path.

**Core families:**

| CORE_VERSION | Core |
|---|---|
| `$10` | FX v1.xx (extended graphics + blitter + palette) |
| `$11` | GTIA emu v1.xx (GTIA-compatible only, no FX extras) |
| other | Reserved / unknown |

Four FX hardware variants are available: `a` (standard XL/XE), `r` (RAMBO 256K internal), `5200` (`g` suffix), and `g` without RAMBO.

## 15.2 FX Core Specs

VBXE FX core v1.26 — hardware capabilities:

| Feature | Value |
|---|---|
| VRAM | 512 KB local (14 MHz bus, 8× ANTIC bandwidth) |
| Palette | 21-bit RGB (7-bit per channel) = 2 097 152 colours; 4 planes × 256 entries (1024 simultaneously) |
| Overlay modes | SR 320/336×256c; HR 640×16c; LR 160×256c; text 80-col |
| XDL | Independent display list; no JVB or CPU rewrite needed per frame |
| Attribute map | 8×1 – 32×32-pixel cells (G8 resolution); 32 colour sets; scroll in X/Y |
| Blitter | 14 MHz; copy/fill; 6.75 MB/s copy, 13.5 MB/s fill; IRQ on completion |
| Sprites | 1×1 – 256×256 G8-sized; 256 colours each; quantity limited by blitter throughput |
| Priority | Programmable per-layer (PM0–PM3, PF0–PF3, COLBAK, overlay) |
| RAMBO core | 320 KB expansion via PORTB banking; upper 256 K bonded at $4000 |

VBXE 1.0 introduced the board; VBXE 2.0 cut initialisation from ~6 s to <1 s. By November 2010 roughly 125 of version 2.0 had been sold.

## 15.3 Register Layout

VBXE registers at `$D600` (slot 0) or `$D700` (slot 1) block.

| Reg | R/W | Description |
|---|---|---|
| `$D600` | W | VIDEO_CONTROL — primary mode/effect register |
| `$D601/$D602` | W | XDL pointer low/high |
| `$D60C/$D60D/$D60E` | W | CR/CG/CB — palette RGB |
| `$D618` | W | XDLC — XDL control bits |
| `$D62E/$D62F` | W | MEMAC A window (0x3000 or 0x4000 base) |
| `$D61D` | RW | MEMAC B control (FX 1.20+) |
| `$D61F` | R | FX magic word = $10 |
| `$D620` | R | FX revision byte (BCD; bit 7 = RAMBO) |

### FX CORE registers ($D640–$D65F and $D740–$D75F)

| Reg | Write | Read |
|---|---|---|
| `$Dx40` | VIDEO_CONTROL | CORE_VERSION |
| `$Dx41` | XDL_ADR0 | MINOR_REVISION |
| `$Dx42` | XDL_ADR1 [7:0] | `$FF` |
| `$Dx43` | XDL_ADR2 [15:8] | `$FF` |
| `$Dx44` | CSEL (palette select 0–3) | `$FF` |
| `$Dx45` | PSEL (playfield palette) | `$FF` |
| `$Dx46` | CR red | `$FF` |
| `$Dx47` | CG green | `$FF` |
| `$Dx48` | CB blue | `$FF` |
| `$Dx49` | COLMASK entry mask | `$FF` |
| `$Dx4A` | COLCLR write-back | COLDETECT read-out |
| `$Dx4B–$Dx4F` | reserved | `$FF` |
| `$Dx50` | BL_ADR0 blitter src/dst | BLT_COLLISION_CODE |
| `$Dx51` | BL_ADR1 blitter list | `$FF` |
| `$Dx52` | BL_ADR2 | `$FF` |
| `$Dx53` | BLITTER_START | BLITTER_BUSY |
| `$Dx54` | IRQ_CONTROL | IRQ_STATUS |
| `$Dx55–$Dx5C` | P0–P3 + reserved | `$FF` |
| `$Dx5D` | MEMAC_B_CONTROL | `$FF` |
| `$Dx5E` | MEMAC_CONTROL | MEMAC_CONTROL (read-back) |
| `$Dx5F` | MEMAC_BANK_SEL | MEMAC_BANK_SEL |

> x = 6 or 7 depending on which page VBXE is decoded at.

**GTIA emu core** (`CORE_VERSION = $11`): `$Dx40–$Dx48`, `$Dx4A` are write; rest read as `$FF`.

---

## 15.4 VBXE Detection

### FX core 1.20+ (KMK/DLT, 2009)

```asm
MEMAC_B_CTL = $5d
vbxe_detect
        lda   #$d6
        sta   _vbxe_write+2
        ldy   #MEMAC_B_CTL
        jsr   ?clr
        jsr   ?try
        bcc   ?ret
        inc   _vbxe_write+2
?try    ldx   $4000
        jsr   ?chk
        bcc   ?ret
        inx
        stx   $4000
        jsr   ?chk
        dec   $4000
?ret    rts
?chk    lda   #$80
        jsr   _vbxe_write
        cpx   $4000
        beq   ?clr
        clc
?clr    lda   #$00
_vbxe_write
        sta   $d600,y
        rts
```

Return: **C=0** → VBXE found; `_vbxe_write+2` = `$D600` or `$D700`.

### Core version < 1.20

KMK/DLT code above uses `MEMAC_B_CTL = $4c` for cores older than 1.20. Detection logic unchanged.

### FX revision read

```asm
        ; run after vbxe_detect
        ; out: C=0 FX core confirmed, vb_rev=BCD revision,
        ;      vb_rambo bit 7 set when FX 1.21+ RAMBO core is present

get_fx_version
        lda   #$00
        sta   vb_rambo
        sta   vb_page
        lda   _vbxe_write+2
        sta   vb_page+1
        ldy   #$40
        lda   (vb_page),y    ; CORE_VERSION ($D640 or $D740)
        cmp   #$10
        bne   not_fx
        iny
        lda   (vb_page),y    ; CORE_REVISION
        cmp   #$ff
        beq   not_fx
        asl
        ror   vb_rambo       ; bit 7 = RAMBO flag
        lsr
        sta   vb_rev          ; BCD revision byte
        clc                   ; FX OK
        rts
not_fx  sec
        rts
```

Return: **C=0** → FX core confirmed; `vb_rev` = BCD revision; bit 7 of original byte = RAMBO flag (`vb_rambo`).

**Revision byte structure** (valid from FX 1.21):
- bit 7 = 1 → RAMBO core
- bits 6–4 → BCD major revision (values 0–7)
- bits 3–0 → BCD minor revision (values 0–9)
- Compatible cores have bits 6–4 equal (FX 1.20 software runs on 1.24).

FX 1.20 predates the RAMBO bit and must be detected by comparing PORTB-selected and MEMAC-selected banks separately. Cores before 1.08 return `$FF` at CORE_REVISION.

---

## 15.5 XDL and Minimal Init

XDL is VBXE's extended display list. It controls overlay mode, palette selection, priority, scrolling, and attribute-map behavior independently from ANTIC's display list.

Minimal setup path:

1. Detect VBXE and record whether it decodes at `$D600` or `$D700`.
2. Disable or stabilize display changes while programming registers.
3. Upload palette entries through `CSEL/PSEL` and `CR/CG/CB`.
4. Place the XDL in CPU-visible memory or VRAM as required by the selected mode.
5. Write XDL address registers.
6. Enable XDL processing through `VIDEO_CONTROL/XDLC`.

XDL design rules:

- Keep XDL state changes at stable scan-line boundaries.
- For interlace or field-dependent effects, use paired entries and avoid one-scan-line toggles unless the effect is intentionally unstable.
- Treat VBXE overlay priority separately from GTIA player/playfield priority.

## 15.6 VRAM, MEMAC, Palette, and Blitter

VBXE has 512 KB of local VRAM. The CPU accesses it through MEMAC windows and the blitter.

| Mechanism | Use |
|---|---|
| MEMAC A | CPU-visible VRAM window, commonly at `$3000` or `$4000` depending on setup |
| MEMAC B | Additional/banked window and detection/control path on newer FX cores |
| Palette registers | 21-bit RGB entries selected through palette index/control registers |
| Blitter list | Copy/fill/attribute operations executed by VBXE hardware |
| Blitter busy/IRQ | Poll or interrupt on completion before reusing blitter state |

Blitter workflow:

1. Build a blitter command/list in the expected format for the FX core.
2. Point blitter address registers at the command/list.
3. Start the blitter.
4. Poll `BLITTER_BUSY` or handle the blitter IRQ.
5. Do not overwrite source, destination, or command memory until complete.

Common hazards:

- FX core revisions before 1.20 differ in MEMAC B behavior.
- Register base can be `$D600` or `$D700`; never hard-code one after detection found the other.
- VRAM writes through a MEMAC window are bank/window-relative, not CPU-linear.
- Palette and XDL changes can tear if made mid-frame without a planned raster boundary.

## 15.7 EN Code Examples (Index)

> ⚠ **XDL/blitter I-field annotation:** Annotation-decoder such as screen-swap overlap, colour-lut reload, and sprites that reference attribute-map cells from even/odd VBLANK halves require frame-doubling XDL sequences (wide XDL entries must be ≥2 NTSC scanlines thick for wobble-free 60 Hz; single-scanline XDL triggers a carry-in hazard on the blitter pixel counter). Production examples below use Ψ-annotated XDL tables where the Ψ character marks paired I-field state transitions.
> ⚠ **MEMAC A/B window hazard:** On FX firmware < 1.20, MEMAC B_CTL ($D61D) does not expose the auto-increment burst bit. Detection routines that probe MEMAC_B_CTL against $80 must gate on CORE_VERSION ≥ $11 before trusting the response.

### Candle Family

| File | Description |
|------|-------------|
| Candle/1200xl/a1200xl.asm | 1200XL logo replacement; RMT music; inflate; MEMAC A @0x3000; palette fade |
| Candle/scroll/scroll.asm | Sinus H/V scroll via XDL; cross-fade between VRAM pages |
| Candle/slideshow/slide.asm | 16-DAP image slideshow; blitter fades, palette switching |

### Electron Family

| File | Description |
|------|-------------|
| Electron/bt.asm | 80-col text H-scroll demo; blitter scroll, rnd foreground colour |
| Electron/cmap.asm | Attribute map gradient demo; MEMAC B + blitter |
| Electron/mtest1.asm | CPU→VRAM write/readback integrity test |
| Electron/mtest2.asm | Dual-bank VRAM write/readback test |
| Electron/vbmp.asm | 320×200 256-col BMP file browser via blitter DAP |
| Electron/vbxefx.asm | FX macros + palette for MADS |
| Electron/scroll/sk1.asm | Full scroller demo; sinus fonts over plasma |

### KMK / Fox / Rybags / Other

| File | Description |
|------|-------------|
| `KMK/textmode.s` | 80×24/80×32 text mode; cursor, Tab⇒colour, inverse video via blitter |
| `KMK/dactest.s` | DAC test; blitter fill, BCB chain, 4-palette setup |
| Fox/st2vbxe.asx | ST→VBXE converter demo; xex binary |
| `Rybags/Quadrillion/` | Full game port from Commodore Plus/4; VBXE v1.24+ required |
| `TeBe/plasma/` | Plasma effect; colour map 40×49, sinus tables, XDL raster |

---

Full production builds such as the LAMERS Group `oldschool` directory (10 FX parts) and `wb2` directory (8 FX parts plus bank-switcher) are useful for studying real VBXE asset streaming, XDL changes, and blitter-heavy effects.

Source notes: VBXE detection and register summaries use `Atariki/articles/rejestry_vbxe.md`, `wykrycie_vbxe.md`, `video_board_xe.md`, and the English FX 1.26 manual.
