

# Optimizing Branch Prediction {#sec:ChapterBadSpec}

So far we've been talking about optimizing memory accesses and computations. However, we haven't discussed another important category of performance bottlenecks yet. It is related to speculative execution, a feature that is present in all modern high-performance CPU cores. To refresh your memory, turn to [@sec:SpeculativeExec] where we discussed how speculative execution can be used to improve performance. In this chapter, we will explore techniques to reduce the number of branch mispredictions.

In general, modern processors are very good at predicting branch outcomes. They not only follow static prediction rules but also detect dynamic patterns. Usually, branch predictors save the history of previous outcomes for the branches and try to guess what the next result will be. However, when the pattern becomes hard for the CPU branch predictor to follow, it may hurt performance.

Mispredicting a branch can add a significant speed penalty when it happens regularly. When such an event happens, a CPU is required to clear all the speculative work that was done ahead of time and later was proven to be wrong. It also needs to flush the pipeline and start filling it with instructions from the correct path. Typically, modern CPUs experience from 10 to 20 cycles penalty as a result of a branch misprediction. The exact number of cycles depends on the microarchitecture design, namely, on the depth of the pipeline and the mechanism used to recover from the mispredicts.

Branch predictors use caches and history registers and therefore are susceptible to the issues related to caches, namely three C's:

- **Compulsory misses**: mispredictions may happen on the first dynamic occurrence of the branch when static prediction is employed and no dynamic history is available.
- **Capacity misses**: mispredictions arising from the loss of dynamic history due to a very high number of branches in the program or exceedingly long dynamic pattern.
- **Conflict misses**: branches are mapped into cache buckets (associative sets) using a combination of their virtual and/or physical addresses. If too many active branches are mapped to the same set, the loss of history can occur. Another instance of a conflict miss is false sharing when two independent branches are mapped to the same cache entry and interfere with each other potentially degrading the prediction history.

A program will always experience a non-zero number of branch mispredictions. You can find out how much a program suffers from branch mispredictions by looking at the TMA `Bad Speculation` metric. It is normal for a general-purpose application to have a `Bad Speculation` metric in the range of 5-10\%. Our recommendation is to pay close attention once this metric goes higher than 10\%.

In the past, developers had an option of providing a prediction hint to an x86 processor in the form of an encoding prefix to the branch instruction (`0x2E: Branch Not Taken`, `0x3E: Branch Taken`). This could potentially improve performance on older microarchitectures, like Pentium 4. However, modern x86 processors used to ignore those hints until Intel's RedwoodCove started using it again. Its branch predictor is still good at finding dynamic patterns, but now it will use the encoded prediction hint for branches that have never been seen before (i.e. when there is no stored information about a branch). [@IntelOptimizationManual, Section 2.1.1.1 Branch Hint]

There are indirect ways to reduce the branch misprediction rate by reducing the dynamic number of branch instructions. This approach helps because it alleviates the pressure on branch predictor structures. Compiler transformations such as loop unrolling and vectorization help in reducing the dynamic branch count, though they don't specifically aim at improving the prediction rate of any given conditional statement. Progile-Guided Optimizations (PGO) and post-link optimizers (e.g., BOLT) are also effective at reducing branch mispredictions thanks to improving fallthrough rate (straighten the code). We will discuss those techniques in the next chapter.[^1]

So perhaps the only direct way to get rid of branch mispredictions is to get rid of the branch itself. In subsequent sections, we will take a look at how branches can be replaced with lookup tables, arithmetic, and selection.

[^1]: There is a conventional wisdom that never-taken branches are transparent to the branch prediction and can't affect performance, and therefore it doesn't make much sense to remove them, at least from a prediction perspective. However, contrary to the wisdom, an experiment conducted by authors of BOLT optimizer demonstrated that replacing never-taken branches with equal-sized no-ops in a large code footprint application, such as Clang C++ compiler, leads to approximately 5\% speedup on modern Intel CPUs. So it still pays to try to eliminate all branches.
