---
name: atari8bit-code-examples
description: >-
  Atari 8-bit code catalog — sieve, Tetris engine, RLE depacker, GTIA9++ boilerplate, 40x40 CHBASE, demoscene index.
---

# 14 — Code Examples & Demoscene Catalog

> **Scope:** Working code examples + Atari demoscene catalog: 128B, 256B, 1024B productions; graphics, sound, math, and data-format examples
> **Key items:** sieve, Tetris (1065bIPS engine), RLE depacker, GTIA9++ boilerplate, 40x40 CHBASE, demoscene index
> **Primary sources:** `atari-documentation/code-examples/`, `atari-documentation/code-examples/demoscene/`, and the user-provided MADS assembler example corpus when available.

## Quick-lookup

| Need | See § |
|---|---|
| Sieve of Eratosthenes | §14.1 |
| Tetris engine (drive-declared LUTs + DLI HUD) | §14.1 |
| RLE encode/decode + Pascal Tebe encoder | §14.2 |
| GTIA mode 9++ display list + DLI color patch | §14.2 |
| 40\u00d740 character-mode CHBASE (TMC v2.00) | §14.2 |
| 128B productions (BeatTheStars, greenmil, rand_walker, waveanim) | §14.3 |
| 256B productions (fire, sintro, water, galactic_bearing, quatari, deform\u2026) | §14.3 |
| 1024B algorytm_v08i (Agenda/svoy, 4 FX sections) | §14.3 |
| Candle/Electron VBXE production file index | §14.4 |
| MADS example corpus map | §14.6 |

## 14.1 Math and Algorithm Examples

### Sieve of Eratosthenes (sieve.asm)

```asm
; AX timing-sync trial prime self-assertive BI
; uses ATAS-style macros; splits timing via wait() VBL
; Breadboard: 2,3,5,7,11.
; fits in 48K; splits timing via delay over 10 iterations of >64
```

### Tetris (tetris.asm, TeBe/Madteam v1.1, 1065 lines)

Complete playable Tetris engine:
- Back-reference: 9-tetromino types with 1–4 rotation states via self-modifying code using `l_klocek/h_klocek/l_test/h_test`
- NMI-driven joypad reader with debounce and edge-latch
- Collision detection via `test_posX/Y/faza` jumping to embedded subroutines
- Color text screen with DLI chopping per scanline
- Repeated draws via `mvs` (move n words) macros

---

## 14.2 Graphics Code Examples

### RLE Encode/Decode (rle.asm + rle.pas)

Standard Tebe/MadTeam RLE:
- `getByte` reads from ZP `$ff00,x` auto-increment source pointer
- flag byte LSB=1: literal run; LSB=0: repeat run
- Pascal-side encoder (rle.pas): reads binary, tests each byte odd/even, streams runs

```pascal
procedure save_rle(count, value: byte);
begin
  fout^.write_byte((count-1) shl 1);  // even flag = repeat run
  fout^.write_byte(value);
end;
```

### GTIA Mode 9++ (mode_9++.asm)

Display list: 2 blank lines, then 58× `$8f/$2f` lines (GTIA 9 active at `$2f80`):

```
     .byte $02    ; 2 blank lines
     REPT 58
     .byte $8f, $2f
     ENDR
     .byte $41    ; JVB → display list loop
     .word display_list
```

DLI at scan-line boundary: colour 13 → colour 3 via `sta COLPF0` patching.

### 40×40 Character Mode (40x40.asm)

Copies font from `$8000` to `$8400` on init, then on every scanline: sets `CHBASE = $8000` for even lines, `CHBASE = $8400` for odd lines. Outputs TMC Music Composer v2.00 version string in 40×40 character cells.

```asm
DI   lda   #$00           ; even line: CHBASE = $8000
       sta   CHBASE
       ...
       lda   #$00+$80       ; odd line: CHBASE = $8400
DU   sta   CHBASE
```

### RLE Encode / Pack (`rle_pack`, Tebe/MadTeam)

```asm
; Tebe/MadTeam RLE encoder skeleton
; Walks input bytes, accumulates runs, writes (flag, byte) pairs
; Entry: src = input end; dst = output start
; Exit:  src cleaned: input pointer advanced through end

rle_pack
@read  lda    (src),y
        cmp    last_byte
        bne    @flush_run       ; new byte: flush previous run
        iny
        bne    @read
        inc    src+1            ; cross-page source
        jmp    @read

@new_run
        sty    run_count
        lda    #$00
        clc
        adc    #$02             ; flag = (run_count - 1) << 1 | 0  (repeat flag)
        sta    (dst),y
        lda    last_byte
        sta    (dst),y
        lda    (src),y
        sta    last_byte
        jmp    rle_pack
```

---

## 14.3 Demoscene Catalog

### 128-Byte Productions (demoscene/128B/ (see §14.3 table))

| Production | Author | Year | Technique |
|------------|--------|------|-----------|
| **BeatTheStars** | Ivo van Poorten | 2018 | OST (oscillator stack trace) + PMG0 star cluster |
| **greenmil** | goblinish | — | Colour bar decay from stacked `$0C→$00→$0E` luma ramp |
| **rand_walker** | — | — | OS/9 16-shade random walker (X=stride, Y=stride mod) |
| **waveanim** | — | — | ATASCII character sine wave via OS CIO `PUTBT` on `$D012` |

### 256-Byte Productions (demoscene/256B/ (see §14.3 table))

**Main catalogue:**

| Production | Author | Year | Technique |
|------------|--------|------|-----------|
| **fire** | — | — | GTIA 9 mode buffer, 4-neighbour thermal |
| **galactic_bearing** | Agenda/svoy | 2019 | Fractal turbo; chaos-game superposition |
| **sintro** | MadTeam | 1997 | Cosine generator, `tcos` table (256-point inverse), mirror quads |
| **water** | SeBan/Slight | 2021 | Buffer A/B double-buffer; 4-neighbour averaging; `ADC <rnd` to bottom |
| **quatari** | Ilmenit | 2020 | 4 FX (maze/sierpinski/lights/landscape) share one screen buffer |
| **porazka** | taquart | — | Dual effect: plasma + kefrens propagation, 256-entry LUT, XOR interlace |
| **deform** | pr0be/laresistance | 2004 | Double-buffered DLI at `$2800/$2c00`; raw texture DMA |
| **glenches** | pr0be | — | 3D wireframe using precomputed `xtab`, `bitmask`, `sqrtab` lookup tables |
| **LANDSCAPE** | tr1x/Agenda | 2021 | Procedural mountains via `f=(f-1)*x` product; stars as PMG0 clusters |

**Kefrens interlace subdir (`kefrens/`):**

| File | Technique |
|------|-----------|
| `kefrens_1st_twt.xsm` | Blank every 2nd line; LIFO sine-start offsets (stack `PLA/ADC` pairs) |
| `kefrens_interlaced.xsm` | Dual LUT `$600/$680`; fixed offset `+$11` per pixel; XOR interlace via `eor #1` |
| `kefrens_final.xsm` | Solid lines; `make_dl` build-time DLI at `$2000`; `inc $d500,x` for scanline sync |

### 1024-Byte Productions (demoscene/1024B/ (see §14.3 table))

**algorytm_v08i.asm (Agenda/svoy, Forever 2019, 766 lines)** — 4 FX sections:

| FX | Mechanism |
|----|-----------|
| fx1_vbl | GTIA mode cycling; PMG0 bar copy; square logo |
| fx2_vbl | Full-mode picture; charset swap + mirror raster |
| fx3_vbl | Randomized DLI + rapid BG colour cycling |
| fx4_vbl | Character-set scrambling; PMG0 rotation |

All sections driven by `<RUN_L / EXIT_L>` and `<RUN_H / EXIT_H>` address tables. Full RMT music engine with 4 channels (kickbas/sndkick5/sndkick6 + seclead + leadnotes).

---

## 14.4 Candle/Electron VBXE Production Files

| File | FX / Technique |
|------|----------------|
| Candle/scroll/scroll.asm | Horizontal/vertical sinus scroll via XDL; cross-fade between VRAM pages |
| Electron/scroll/sk1.asm | Full scroller: sinus fonts over plasma background |

*Note: full VBXE production detail including Candle/1200xl (logo replacement, RMT, inflate, MEMAC A), slideshow, Candle/slideshow, and Electron/vbmp.asm is in the VBXE reference file in the Atari 8-bit skill collection.*

---

## 14.6 MADS Example Corpus Map

Use the user-provided MADS examples corpus when a task needs runnable MADS idioms rather than isolated algorithms. If the corpus location is not obvious, ask the user for the path.

| Area | Files to inspect | Useful pattern |
|---|---|---|
| Syntax and scoping | `if_else.asm`, `while.asm`, `rept.asm`, `local*.asm`, `macro_proc_local.asm`, `struct_enum.asm` | Compile-time control, local namespaces, macro-local labels, typed structures. |
| Loaders and file I/O | `Boot.asm`, `file_loader.asm`, `file_header.asm`, I/O and stdio library examples | Boot sectors, dual-address relocation, CIO-style library calls, command-line parsing. |
| Banking and detection | `xms_banks.asm`, `detect_memory.asm`, `detect_cpu.asm`, `detect_sdx.asm`, `stereo_detect.asm` | 130XE/RAMBO bank setup, CPU and SDX capability probes, stereo POKEY detection. |
| Raster graphics | MCP DLI/IRQ, MAX viewer, mode 9++, and 40x40 examples | DLI/IRQ colour splits, interlace modes, VSCROL/CHBASE timing. |
| Compression | RLE, LZ4, Exomizer, and NuCrunch examples | Depacker loop structure and workspace trade-offs. |
| Music players | Tracker relocator and ProTracker examples | Relocatable RMT/MPT/CMC/TMC players and module-data inclusion. |

Treat `.obx`, `.lst`, and `.lab` beside source files as verification artifacts: use listings and labels to confirm generated addresses, but summarize techniques from source in English.

---

## 14.5 Demo Skeleton Template

```asm
; Demo skeleton: init -> deferred VBI + DLI -> main loop
; Target machine type: Atari XL/XE, MADS assembler

        .org   $2000            ; standard XEX load address

; ============================================================
; INIT
; ============================================================
init
        sei                    ; mask IRQs during init
        lda    #$00
        sta    NMIEN            ; disable DLI/VBI during setup

        ; set up display list
        lda    #<display_list
        sta    SDLSTL            ; OS shadow: $0230
        lda    #>display_list
        sta    SDLSTL+1

        ; set up deferred VBI through the OS
        ldy    #<my_vbi
        ldx    #>my_vbi
        lda    #$07              ; deferred VBI slot
        jsr    SETVBV

        ; set up DLI vector. VDSLST is DLI-only, not VBI.
        lda    #<my_dli
        sta    VDSLST
        lda    #>my_dli
        sta    VDSLST+1

        ; enable VBI + DLI
        lda    #$C0             ; $40=VBI, $80=DLI
        sta    NMIEN

        ; Zero page init
        ldx    #$00
@zloop  lda    #$00
        sta    zpage,x
        inx
        bne    @zloop

        cli                    ; re-enable IRQs
        ; fall through to main loop

; ============================================================
; MAIN LOOP
; ============================================================
main_loop
        ; per-frame work here (input -> update -> render -> VBI swap)
        jmp    main_loop

; ============================================================
; VBI
; ============================================================
my_vbi
        ; per-frame deferred work:
        ;   - update scroll accumulators
        ;   - swap display-list pointers
        ;   - clear VSCROL/HSCROL shadow state
        jmp    XITVBV            ; correct deferred VBI exit path

; ============================================================
; DLI
; ============================================================
my_dli
        pha
        txa
        pha
        tya
        pha
        sta    WSYNC             ; align visible register writes
        ; write hardware color/GTIA/ANTIC registers here, not shadows
        pla
        tay
        pla
        tax
        pla
        rti

; ============================================================
; Data
; ============================================================
display_list
        .byte  $70,$70,$70       ; 3 blank lines (top border)
        .byte  $4C               ; JVB -> loop
        .word  display_list
```

---

## 14.6 MADS `.STRUCT` / `.PROC` / `.RELOC` / 65816 `.A8` Example

```asm
; MADS structures and procedures
; .STRUCT: packed memory layout
; .PROC: typed parameters + @CALL/@PUSH/@PULL/@EXIT
; 65816: .A8 / .A16 accumulator modes

        .proc  InitDisplayList args(display_list_addr)
@call   mwa    #display_list display_list_addr
@exit   rts
        .endp

        .struct Vert3d
x       .byte
y       .byte
z       .byte
        .ends

        .a8                    ; 8-bit accumulator
        lda    #$4C
        .a16                   ; 16-bit accumulator
        lda    #$1234
```
