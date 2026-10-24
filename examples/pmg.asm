; Runnable XEX: 64K XL/XE, OS on, default screen, no pre-existing PMG engine.
; P0 at x=100, 32 single-scanline rows; START exits and disables PMG.
; Reserves $4000-$47FF (2K aligned); no private ZP. Other players/missiles zero.
; Entry contract: PMG disabled; SIZEP0=0, PRIOR=0. Color/DMA shadow restored.
        icl 'atari.inc'
        org $2000
start
        cld
        lda SDMCTL
        sta saved_dma
        lda PCOLR0
        sta saved_color
        ; DS reserves addresses but does not initialize RAM in an XEX.
        ; Clear every DMA page before enabling players, then draw P0's shape.
        lda #0
        tax
clear_pmg
        sta pmg_memory,x
        sta pmg_memory+$100,x
        sta pmg_memory+$200,x
        sta pmg_memory+$300,x
        sta pmg_memory+$400,x
        sta pmg_memory+$500,x
        sta pmg_memory+$600,x
        sta pmg_memory+$700,x
        inx
        bne clear_pmg
        ldx #31
        lda #$ff
draw_player
        sta player0+80,x
        dex
        bpl draw_player
        lda #$40
        sta PMBASE              ; high byte of $4000
        lda #0
        sta SIZEP0
        sta PRIOR
        lda #$3e
        sta PCOLR0
        lda #100
        sta HPOSP0
        lda #2
        sta GRACTL              ; enable player graphics
        lda saved_dma
        ora #$18                ; single-line player DMA (missiles unused)
        sta SDMCTL
frame
        lda CONSOL
        and #1
        bne frame
cleanup
        lda #0
        sta GRACTL
        sta HPOSP0
        lda saved_dma
        sta SDMCTL
        lda saved_color
        sta PCOLR0
cleanup_return
        rts
saved_dma   .byte 0
saved_color .byte 0

        org $4000
pmg_memory
        .ds $400               ; unused + missile DMA area
player0
        .ds $100
        .ds $300               ; P1-P3 empty
        run start
