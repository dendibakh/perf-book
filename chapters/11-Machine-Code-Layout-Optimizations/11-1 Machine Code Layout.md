---
typora-root-url: ..\..\img
---

[TODO]: Describe how to measure code footprint

# Machine Code Layout Optimizations {#sec:secFEOpt}

CPU Front-End (FE) component is discussed in [@sec:uarchFE]. Most of the time, inefficiencies in CPU FE can be described as a situation when Back-End is waiting for instructions to execute, but FE is not able to provide them. As a result, CPU cycles are wasted without doing any actual useful work. Because modern processors are 4-wide (i.e., they can provide four uops every cycle), there can be a situation when not all four available slots are filled. This can be a source of inefficient execution as well. In fact, [`IDQ_UOPS_NOT_DELIVERED`](https://easyperf.net/blog/2018/12/29/Understanding-IDQ_UOPS_NOT_DELIVERED)[^2] performance event is counting how many available slots were not utilized due to a front-end stall. TMA uses this performance counter value to calculate its "Front-End Bound" metric[^1].

The reasons for why FE could not deliver instructions to the execution units can be plenty. But usually, it boils down to caches utilization and inability to fetch instructions from memory. It's recommended to start looking into optimizing code for CPU FE only when TMA points to a high "Front-End Bound" metric.

\personal{Most of the real-world applications will experience a non-zero "Front-End Bound" metric, meaning that some percentage of running time will be lost on suboptimal instruction fetching and decoding. Luckily it is usually below 10\%. If you see the "Front-End Bound" metric being around 20\%, it's definitely worth to spend time on it.}

## Machine Code Layout

When a compiler translates your source code into machine code (binary encoding), it generates a serial byte sequence. For example, for the following C code:
```cpp
if (a <= b)
  c = 1;
```
the compiler could generate assembly like this:
```asm
; a is in rax
; b is in rdx
; c is in rcx
cmp rax, rdx
jg .label
mov rcx, 1
.label:
```

Assembly instructions will be encoded and laid out in memory consequently:

```asm
400510  cmp rax, rdx
400512  jg 40051a
400514  mov rcx, 1
40051a  ...
```

This is what is called *machine code layout*. Note that for the same program, it's possible to lay out the code in many different ways. For example, given two functions: `foo` and `bar`, we can place `bar` first in the binary and then `foo` or reverse the order. This affects offsets at which instructions will be placed in memory, which in turn may affect the performance of the generated binary. For the rest of this chapter, we will take a look at some typical optimizations for the machine code layout.

[^1]: See exact formulas in TMA metrics table: [https://download.01.org/perfmon/TMA_Metrics.xlsx](https://download.01.org/perfmon/TMA_Metrics.xlsx).
[^2]: See more information about this performance event here: [https://easyperf.net/blog/2018/12/29/Understanding-IDQ_UOPS_NOT_DELIVERED](https://easyperf.net/blog/2018/12/29/Understanding-IDQ_UOPS_NOT_DELIVERED)
