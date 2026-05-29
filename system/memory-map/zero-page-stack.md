# Zero Page Stack

## 2.4  Zero-Page Idioms

| Idiom | Example | Notes |
|---|---|---|
| Increment/decrement 16-bit (hi carries if lo overflows) | `INC ptr: INC ptr+1: BNE skip` / `DEC ptr+1: BNE skip` | `INC/DEC ZP` takes 5 cycles, RMW side effect |
| Bit flag set/clear | `ORA #$80` / `AND #~$80` | LSB/OMSB of bit-index using `:ROL`, `:LSR`, 7 or 0 |
| Negative-index backwards loop | `LDY #-n: … DEY: BPL loop` | Zero-page table walk backwards wrapped at $00FF |
| Fast ISR scratch save | `STA save_a: STX save_x: STY save_y` | Hardware stack is fastest; ZP shadow nearby |
| 16-bit load with skip | `LDA #<val: STA ptr: LDA #>val: STA ptr+1` | Separate LDA avoids page-cross on HIGH byte |

---

## 2.5  Stack & Subroutine Parameters

6502 stack: 256 bytes at `$0100–$01FF`, `TSX/TXS` to read/write pointer.

**Parameter-inline trick:** A subroutine can read own return-address off the stack to find embedded data tables after the JSR, avoiding zero-page allocation:

```asm
        ; Caller:
        jsr my_routine
        .byte $01, $02, $03   ; data table after JSR

        ; Callee:
my_routine
        pla                  ; pop low byte of return PC
        sta data_ptr
        pla                  ; pop high byte
        sta data_ptr+1
        ; Now data_ptr → .byte table past JSR
        rts
```

---

*Content fully self-contained. All key facts are present in this file.
