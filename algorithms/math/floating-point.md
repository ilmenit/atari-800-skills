# Floating Point

## 10.8 Floating-Point Entry

Atari programs normally avoid floating point in inner loops. If FP is required,
use the OS floating-point package entry points rather than copying a large FP
runtime into a skill example. The practical rule is: convert once at the edge,
cache fixed-point values, and keep render/audio/game loops in integer or 8.8
fixed-point arithmetic.

---
