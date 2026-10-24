# Read-Modify-Write and Hardware Registers

NMOS 6502 INC/DEC/ASL/LSR/ROL/ROR on memory read the old value, write that old
value back, then write the modified value. Zero-page INC/DEC occupy two bytes
and take five CPU cycles; absolute INC/DEC occupy three bytes and take six,
before DMA stalls. Arithmetic wraps modulo 256 and updates N/Z; INC/DEC leave
carry unchanged.

Hardware read and write meanings can differ at the same address. For example,
`$D208` reads ALLPOT but writes AUDCTL. `INC $D208` therefore does not safely
increment a stored AUDCTL configuration. NMIEN is write-only, so reading it as
part of INC/DEC does not recover the previous enable mask. A write to NMIRES
clears NMI status; it does not generate a new NMI.

Use a software shadow or a known configuration and an explicit store:

```asm
; Partial snippet: caller owns NMI configuration and initialized VDSLST.
        lda nmi_mask
        ora #$80
        sta nmi_mask
        sta NMIEN
```

Account for both writes before deliberately using an RMW instruction on I/O.
CMOS CPU variants have different bus-cycle details; do not infer portable
hardware side effects from the NMOS sequence.

Source: [Altirra Hardware Reference Manual](https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf),
CPU bus cycles and AUDCTL/ALLPOT/NMIEN/NMIRES register descriptions.
