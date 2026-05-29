# Rmw Inc Dec

## 11.1 INC / DEC and Zero-Page Read-Modify-Write

### RMW on zero page

`INC <addr>` and `DEC <addr>` are single-byte instructions on zero page that perform a read-modify-write cycle inside the chip. They honour the bit-7 wrap for `INC` and underflow for `DEC`:

```asm
zp_inc  equ $80
zp_dec  equ $81

        inc   zp_inc          ; NZ flags set from result
        dec   zp_dec          ; NZ flags set from result
```

### INC / DEC on hardware registers — AUDCTL and NMIEN

Writing to `AUDCTL ($D208)` with `INC` or `DEC` increments/decrements the high-frequency timer divisor. On `NMIEN ($D40E)`, `INC` pulls NMI masking bits into the DLI enable (DLI active high), and `DEC` turns them back off.

**INC NMIRES trick (quick-enable NMI):**

Writing any value to `NMIRES ($D40F)` immediately cause NMI to fire if it is not currently masked. Pairing `INC NMIRES` with the NMI/IRQ flip can save one cycle in the ISR for 400/800 event loop needs.

**Practical INC/DEC patterns:**
```asm
        inc   $d40e            ; unblock NMI/DLI
        dec   $d40e            ; block NMI/DLI
```

---
