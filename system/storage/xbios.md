# Xbios

## §7.7  xBIOS — Mini-OS File Access

xBIOS is a compact disk I/O layer that can run from low memory and provides file read/write without the full DOS overhead.

**What xBIOS provides:** open, read, write, seek, and file-size query through SIO-compatible structures. It is useful for compact loaders and games that need file access without keeping a full DOS resident.

**DCB access for xBIOS:** identical to standard Atari 810 SIO DCB format: $09 command / $0A AUX1 / $0B AUX2; uses the same serial bus protocol as Atari DOS — xBIOS translates IECBUS calls to SIO internally by passing the DCB directly, then uses the OS handler sequence `SIOV` to call and poll.

```asm
                ; xBIOS-style DCB init for READ — file already on disk/drive_1_unit
                ; dcb must be in zero page for rapid SIO access

dcb_dev     = $00           ; device ID (e.g. $31 for drive-1)
dcb_cmd     = $02           ; $52 = read record
dcb_aux1    = $03           ; buffer address low
dcb_aux2    = $04           ; buffer address high
dcb_buf_lo  = $05           ; buffer page-lo (page aligned preferred)
dcb_buf_hi  = $06           ; buffer page-hi
dcb_len     = $09           ; buffer length (2-byte)

init_xbios_read
        lda #$31               ; DDEVIC = drive 1, SIO device
        sta dcb_dev
        lda #$52               ; DCMD = $52 (read-sector / get-verify record)
        sta dcb_cmd
        lda #<read_buffer
        sta dcb_aux1
        lda #>read_buffer
        sta dcb_aux2

        jsr SIOV               ; $E459 — call SIO handler via OS vector
        bcs ?error             ; carry = SIO error
        ; ... read_buffer now holds the sector
?error  rts

; read_buffer must be sector-aligned: 128 bytes for SD disks (Atari 810 format)
```

**xBIOS vs native CIO:** CIO is the OS-level handler layer (`CIOV`); SIO is the serial-bus layer (`SIOV`). xBIOS bypasses standard DOS file handling and uses SIO-compatible access patterns with a smaller runtime API.

---

---
