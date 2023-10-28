---
typora-root-url: ..\..\img
---

[TODO]: fix the beginning

# Optimizing Branch Prediction

The speculation feature in modern CPUs is described in [@sec:SpeculativeExec]. Mispredicting a branch can add a significant speed penalty when it happens regularly. When such an event happens, a CPU is required to clear all the speculative work that was done ahead of time and later was proven to be wrong. It also needs to flush the whole pipeline and start filling it with instructions from the correct path. Typically, modern CPUs experience a 15-20 cycles penalty as a result of a branch misprediction.

Nowadays, processors are very good at predicting branch outcomes. They not only can follow static prediction rules[^1] but also detect dynamic patterns. Usually, branch predictors save the history of previous outcomes for the branches and try to guess what will be the next result. However, when the pattern becomes hard for the CPU branch predictor to follow, it may hurt performance. One can find out how much a program suffers from branch mispredictions by looking at TMA `Bad Speculation` metric.

\personal{A program will always take a non-zero number of branch mispredictions. It is normal for general purpose applications to have a "Bad Speculation" rate in the range of 5-10\%. My recommendation is to pay attention to this metric if it goes higher than 10\%.}

Since the branch predictors are good at finding patterns, old advice for optimizing branch prediction is no longer valid. One could provide a prediction hint to the processor in the form of a prefix to the branch instruction (`0x2E: Branch Not Taken`, `0x3E: Branch Taken`). While this technique can improve performance on older platforms, it won't produce gains on newer ones[^2].

Perhaps, the only direct way to get rid of branch mispredictions is to get rid of the branch itself. In the two subsequent sections, we will take a look at how branches can be replaced with lookup tables and predication.

[^1]: For example, a backward jump is usually taken, since most of the time, it represents the loop backedge.
[^2]: Anything newer than Pentium 4.
