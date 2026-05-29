# Collisions

## §4.8  Collision Detection

| Register | Read | Collision type |
|---|---|---|
| `$D000` / M0PF | Missile 0 ↔ Playfield | Missile-to-playfield |
| `$D004` / P0PF | Player 0 ↔ Playfield | Player-to-playfield |
| `$D008` / M0PL | Missile 0 ↔ Player | Missile-to-player |
| `$D00C` / P0PL | Player 0 ↔ Player | Player-to-player |

**Clear:** write any value to HITCLR (`$D01E`); clears ALL collision flags simultaneously. (Keep track of which bits were set before the write to distinguish between collisions.)

```asm
        lda M0PF              ; $D000 — did missile 0 hit background?
        pha
        lda P0PF              ; $D004 — did player 0 hit background?
        pha
        lda M0PL              ; $D008 — did missile 0 hit any player?
        pha
        lda P0PL              ; $D00C — did any player-to-player collision fire?
        pha
        lda #$00
        sta HITCLR            ; $D01E — clear ALL collision flags
        pla                   ; P0PL → A  
        sta collision_p0pl
        pla                   ; M0PL → A
        sta collision_m0pl
        pla                   ; P0PF → A
        sta collision_p0pf
        pla                   ; M0PF → A
        sta collision_m0pf
```

---

Source notes: GTIA register behavior is summarized from `Altirra-hardware/extracted_chapters/chapter06.md` and `atari-documentation/ANTIC-GTIA/GTIA-Registers.md`. Deep DLI patterns live in `hardware/antic.md` and `graphics/display-lists.md`.
