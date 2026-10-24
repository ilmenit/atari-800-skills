; OS on. Out: C=0 and X=free IOCB offset ($10..$70); C=1 if none.
; Preserves Y. Clobbers A/X/N/Z/C. No scratch, no writes to OS variables.
; IOCB0 belongs to the screen editor; callers OPEN a returned slot before use.
find_free_iocb
        ldx #$10
find_iocb_loop
        lda $0340,x             ; ICHID, not ICSTA
        cmp #$ff
        beq find_iocb_found
        txa
        clc
        adc #$10
        tax
        cpx #$80
        bne find_iocb_loop
        sec
        rts
find_iocb_found
        clc
        rts
