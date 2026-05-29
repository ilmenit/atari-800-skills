# Reset

## 2.2  Power-On / Reset

| Condition | Behavior |
|---|---|
| Warm boot (400/800) | RNMI → OS `$FED6` — warm-start, keeps RAM |
| Cold boot (all) | RESET line → `$FFFC` vector; all registers undefined |
| PIA on 400/800 | Only reset on power-on; not by RESET key |
| PIA on XL/XE | Reset on power-on AND RESET key; all regs cleared to $00 |

**RAM power-up bias:** DRAM decays after power-off → power-on produces block patterns (often `$00/$FF` alternating). Treat RAM as undefined until explicitly initialized.

**Floating data bus:** On 800 (secondary I/O bus), on XL/XE without pull-ups: un-decoded reads return the last byte on the data bus (often from the *previous* cycle). On XL/XE with pull-ups: undecoded reads return `$FF`.

---
