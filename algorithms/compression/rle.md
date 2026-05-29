# Rle

## 12.1 RLE — Run-Length Encoding

Tebe/MadTeam format (Konop/Probe/TeBe/Seban):
- Packed byte is POST'ed (least-significant-bit = `1`) for **literal** runs; LSB=`0` for **repeat** runs.
- The run-length decoder reads flag bytes and branches:
  - Flag LSB=1 → read literal bytes (count = flag >> 1 + 1)
  - Flag LSB=0 → read one target byte and repeat (count = flag >> 1 + 2)

**RLE depacker skeleton:**

```asm
        ; ZP: src_ptr = input pointer, dst_ptr = output pointer
        ; dfw_flag = current flag byte
rle_unpack
        jsr    getByte          ; reads from src_ptr
        sta    dfw_flag

        lsr                    ; test flag LSB
        bcs    @literal         ; LSB=1 → literal run
        ; --- repeat run ---
        jsr    getByte          ; read byte to repeat
        lsr    dfw_flag         ; shift flag right (÷2)
        beq    @end_flag        ; flag was 0 → repeat byte once, done
@rptlp  sta    (dst_ptr),y      ; output byte existing, counts 2
        dey
        bpl    @rptlp
        jmp    rle_unpack

@literal lsr    dfw_flag
        beq    rle_unpack
@litlp  jsr    getByte
        sta    (dst_ptr),y
        dey
        bpl    @litlp
        jmp    rle_unpack
```

### 12.1.2 Encoder cross-check

The encoder emits one control byte followed by either a literal sequence or one
repeated byte. The decoder must accept a zero control byte as end-of-stream.

```text
if run_len >= 2:
    emit ((run_len - 2) << 1) | 0
    emit repeated_byte
else:
    emit ((literal_len - 1) << 1) | 1
    emit literal_len bytes
emit 0
```

---
