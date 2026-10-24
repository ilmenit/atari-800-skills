; Runnable XEX: 64K XL/XE, OS on, standard OS VBI, no existing custom DLI.
; ANTIC E: 160x192, four colors, two 3840-byte blocks at $4000/$5000.
; DLI changes PF0 halfway down; deferred VBI counts frames. START exits.
; Claims NMI/display while active. Saves/restores display/vector/color shadows.
; No ZP allocation. $4000-$5EFF must not hold resident DOS/code/assets.
        icl 'atari.inc'
        org $2000
start
        cld
        lda #0
        sta NMIEN
        lda SDMCTL
        sta saved_dma
        lda SDLSTL
        sta saved_dl
        lda SDLSTL+1
        sta saved_dl+1
        lda VDSLST
        sta saved_dli
        lda VDSLST+1
        sta saved_dli+1
        lda VVBLKD
        sta saved_vbi
        lda VVBLKD+1
        sta saved_vbi+1
        ldx #4
save_colors
        lda COLOR0,x
        sta saved_colors,x
        dex
        bpl save_colors
        lda #<display_list
        sta SDLSTL
        sta DLISTL
        lda #>display_list
        sta SDLSTL+1
        sta DLISTL+1
        lda #<my_dli
        sta VDSLST
        lda #>my_dli
        sta VDSLST+1
        ldx #>my_vbi
        ldy #<my_vbi
        lda #7
        jsr SETVBV
        lda #$28
        sta COLOR0
        lda #$86
        sta COLOR1
        lda #$ce
        sta COLOR2
        lda #0
        sta COLOR4
        lda #$22
        sta SDMCTL
        sta DMACTL
        lda #$c0
        sta NMIEN
main
        lda CONSOL
        and #1
        bne main
cleanup
        lda #0
        sta NMIEN
        lda saved_dl
        sta SDLSTL
        sta DLISTL
        lda saved_dl+1
        sta SDLSTL+1
        sta DLISTL+1
        lda saved_dli
        sta VDSLST
        lda saved_dli+1
        sta VDSLST+1
        ldx saved_vbi+1
        ldy saved_vbi
        lda #7
        jsr SETVBV
        ldx #4
restore_colors
        lda saved_colors,x
        sta COLOR0,x
        dex
        bpl restore_colors
        lda saved_dma
        sta SDMCTL
        sta DMACTL
        lda #$40                ; known entry contract: standard OS VBI
        sta NMIEN
cleanup_return
        rts

my_vbi
        inc frame_count         ; A/X/Y already saved by OS
        jmp XITVBV
my_dli
        pha                     ; only A is changed by this DLI
        lda #$48
        sta WSYNC
        sta COLPF0
        pla
        rti

frame_count  .byte 0
saved_dma    .byte 0
saved_dl     .word 0
saved_dli    .word 0
saved_vbi    .word 0
saved_colors .ds 5

        .align $400             ; all display-list fetches within one 1K block
display_list
        .byte $70,$70,$70
        .byte $4e
        .word bitmap_top
        :94 .byte $0e
        .byte $8e               ; DLI on final row of first 96-line half
        .byte $4e
        .word bitmap_bottom
        :95 .byte $0e
        .byte $41
        .word display_list
display_list_end

        org $4000
bitmap_top
        :3840 .byte $55          ; four pixels of color PF0 per byte
        org $5000
bitmap_bottom
        :3840 .byte $55
        run start
