## 2.2  Power-On / Reset

| Condition | Behavior |
|---|---|
| Warm boot (400/800) | RNMI → OS `$FED6` — warm-start, keeps RAM |
| Power-on | CPU RESET vector at `$FFFC/$FFFD`; initialize RAM and software state before use |
| PIA on 400/800 | Only reset on power-on; not by RESET key |
| PIA on XL/XE | Reset on power-on AND RESET key; all regs cleared to $00 |

**RAM power-up bias:** DRAM decays after power-off → power-on produces block patterns (often `$00/$FF` alternating). Treat RAM as undefined until explicitly initialized.

**Floating data bus:** On 800 (secondary I/O bus), on XL/XE without pull-ups: un-decoded reads return the last byte on the data bus (often from the *previous* cycle). On XL/XE with pull-ups: undecoded reads return `$FF`.

---

See [System Reset and power-on](../os-hardening.md#93-system-reset-and-power-on)
for the distinction between the button reset and cold startup.
