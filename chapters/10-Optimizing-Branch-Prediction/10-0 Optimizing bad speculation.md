---
typora-root-url: ..\..\img
---

[TODO]: fix the beginning

# Optimizing Branch Prediction

The speculation feature in modern CPUs is described in [@sec:SpeculativeExec]. Mispredicting a branch can add a significant speed penalty when it happens regularly. When such an event happens, a CPU is required to clear all the speculative work that was done ahead of time and later was proven to be wrong. It also needs to flush the whole pipeline and start filling it with instructions from the correct path. Typically, modern CPUs experience a 15-20 cycles penalty as a result of a branch misprediction.

Modern processors are very good at predicting branch outcomes. They not only follow static prediction rules[^1] but also detect dynamic patterns. Usually, branch predictors save the history of previous outcomes for the branches and try to guess what will be the next result. However, when the pattern becomes hard for the CPU branch predictor to follow, it may hurt performance. One can find out how much a program suffers from branch mispredictions by looking at TMA `Bad Speculation` metric.

Branch predictors use caches and history registers and therefore are susceptible to the issues pertaining to caches, namely three C's:

- Compulsory misses: mispredictions may happen on the first dynamic occurence of the branch when static prediction is employed and no dynamic history is available.
- Capacity misses: mispredictions arising from the loss of dynamic history due to very high number of branches in the program or exceedingly long dynamic pattern.
- Conflict misses: branches are mapped into cache buckets (associative sets) using a combination of their virtual and/or physical addresses. If too many active branches are mapped to the same set, the loss of history can occur. Another instance of a conflict miss is false sharing when two independent branches are mapped to the same cache entry and interfere with each other potentially degrading the prediction history.

\personal{A program will always take a non-zero number of branch mispredictions. It is normal for general purpose applications to have a "Bad Speculation" rate in the range of 5-10\%. My recommendation is to pay attention to this metric if it goes higher than 10\%.}

Since branch predictors are good at finding patterns, old advice for optimizing branch prediction is no longer valid. One could provide a prediction hint to the processor in the form of a prefix to the branch instruction (`0x2E: Branch Not Taken`, `0x3E: Branch Taken`). While this technique can improve performance on older microarchitectures, it won't produce gains on newer ones.[^2]

One indirect way to reduce branch mispredictions is to straighten the code using source-based and compiler-based techniques. PGO and BOLT are effective at reducing branch mispredictions thanks to improving fallthrough rates that alleviates the pressure on branch predictor structures.

So perhaps the only direct way to get rid of branch mispredictions is to get rid of the branch itself. In the two subsequent sections, we will take a look at how branches can be replaced with lookup tables and predication.

\personal{There is a conventional wisdom that never taken branches are transparent to the branch prediction and can't affect performance, and therefore it doesn't make much sense to remove them, at least from prediction perspective. However, contrary to the wisdom, an experiment conducted by BOLT authors demonstrated that replacing never taken branches with equal-sized no-ops in a large code footprint application (Clang binary) leads to approx. 5\% speedup on modern Intel CPUs. So it still pays to try to eliminate all branches.}

[^1]: For example, a backward jump is usually taken, since most of the time, it represents the loop backedge.
[^2]: Anything newer than Pentium 4.
