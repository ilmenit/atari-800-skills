# Selection

## 18.6 Selection Guide

```
N < 20          ->  Optimal Sort 8/16-bit   (low overhead, linked list)
N = 50-200      ->  Bucket sort 8-way        (TORUS3D pattern; zero comparisons)
N large/unsorted->  Quicksort 16-bit          (add median-of-3 pivot guard)
Nearly sorted   ->  CombSort                  (gap=1 only on last pass)
Tiny code       ->  ShellSort Hibbard         (60 B, no ZP workspace)
```

---
