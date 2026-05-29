# Splines

## 10.13 Quadratic Splines for Paths and Curves

Quadratic splines are often enough for game paths, bullet curves, menu motion,
logo outlines, and tweened animation. They are cheaper than cubic splines
because each segment uses three control points instead of four:

```text
P(t) = P0*(1-t)^2 + 2*P1*t*(1-t) + P2*t^2
```

For 6502 code, evaluate with repeated linear interpolation instead of expanding
the polynomial:

```text
A = lerp(P0, P1, t)
B = lerp(P1, P2, t)
P = lerp(A, B, t)
```

With an 8-bit fraction `t = 0..255`, the core operation is:

```text
lerp(a,b,t) = a + ((b-a) * t >> 8)
```

Use the existing 8x8 multiply or a precomputed table when the curve is evaluated
at runtime. For fixed paths, generate points offline or at init and store
screen-space byte coordinates.

To force the curve through three points `s0, s1, s2` at midpoint `t=1/2`, choose:

```text
P0 = s0
P2 = s2
P1 = 2*s1 - (s0+s2)/2
```

Join multiple quadratic segments by sharing endpoints and choosing the next
segment's control point so the tangent direction continues across the join.
For coarse 8-bit animation, a small kink at segment boundaries is usually less
visible than jitter from expensive per-frame math.

Source note: adapted from the portable "Quick Quadratic Splines" article in
C= Hacking issue 20.

---
