# Loaders Depackers

## §7.8 Loader and Depacker Reversing Notes

Use this section with `tooling/reversing.md`.

| Symptom | Likely meaning |
|---|---|
| `SIOV` calls with changing AUX sector numbers | Direct sector loader |
| Writes to `RUNAD` or final indirect `JMP` | Loader transfers to real program |
| `(src),y` and `(dst),y` stream loops | Copy/depack stub |
| Bit-buffer shifts through carry | LZ/DEFLATE-style token reader |
| Writes to `$D301` around `$4000-$7FFF` copies | Extended RAM/banked asset transfer |
| CIO `D:` opens only during init | DOS file load before custom runtime |

Minimum reverse output:

- sector/file source;
- destination address range;
- final entry point;
- whether OS/DOS vectors are restored;
- whether the loader requires a specific DOS, drive, or SIO timing.

## §7.9 MADS Loader Patterns from the Example Corpus

Boot-sector loader, from the MADS example usually named `Boot.asm`:

```asm
        org $0700
boot_hdr
        .word $0001             ; boot sector count, low byte used
        .word boot_hdr          ; load address
        .word $ffff             ; CASINI-related field

        lda #$ff
        sta $d301               ; disable BASIC / map RAM on XL/XE
        lda #1
        sta $0301               ; DUNIT = drive 1
        lda #'R'
        sta $0302               ; DCMD = read
        mwa #main_start $0304   ; DBUF
        mwa #main_sector $030a  ; DAUX sector number

load    jsr $e453               ; SIOV
        bmi error
        adw $0304 #$80          ; next 128-byte buffer
        inw $030a               ; next sector
        ; decrement sector counter...
        jmp load
error   jmp $e477               ; OS SIO error handling path
```

Use this only for ATR/boot-disk workflows. DOS file APIs are not active yet, and the first three boot sectors are normally 128 bytes even on enhanced-density disks.

Dual-address loader stub, from the MADS example usually named `file_loader.asm`:

```asm
source = $2000
dest   = $0700

        org source
        ; copy several pages from source to dest, then jump dest

        org dest,source         ; run as if at dest, store bytes at source
go      ; code that expects to execute at dest
```

This MADS `ORG run,load` form is the correct way to write self-relocating loaders: labels resolve to the execution address, while the bytes are emitted for the file/load address. When reversing, look for early copy loops followed by `JMP dest`; the real code addresses are usually the second `ORG` operand, not the initial file segment address.

The SDX/FAS block tracer example usually named `trace2.fas` is a good model for analyzer tools: read 16-bit block headers, distinguish standard XEX segments from `$FFFA-$FFFE` SDX control blocks, and report update/symbol records rather than flattening the file into raw load ranges.
