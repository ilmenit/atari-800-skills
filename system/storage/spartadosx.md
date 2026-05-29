# Spartadosx

## §7.6  SpartaDOS X Relocatable Code

SDX strips binary into relocatable blocks. The block header types:

```
*dta a($FFFF),a(str_adr),a(end_adr)   ; non-relocatable binary block (standard DOS)
*dta a($FFFA),a(str_adr),a(end_adr)   ; SDX non-relocatable (identifies SDX loader)
*dta a($FFFE),b(blk_num),b(blk_id)
          a(blk_off),a(blk_len)       ; relocatable block
*dta a($FFFD),b(blk_num),a(blk_len)   ; address-update block
*dta a($FFFB),c'SMB_NAME',a(blk_len)  ; symbol update block
*dta a($FFFC),b(blk_num),a(smb_off)
          c'SMB_NAME'                 ; definition block (new symbol)
```

`blk_id` bits: bits 1–5 = memory type ($00=main RAM, $02=ext RAM/RAMBO); bit 7 = absence-of-data flag. The SDX loader computes `new_addr = block_addr_abs + (loaded_addr − blk_off)` for every address field in the relocatable block.

---
