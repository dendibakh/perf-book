---
typora-root-url: ..\..\img
---

## Mispredicted Branch {#sec:BbMisp}

Modern CPUs try to predict the outcome of a branch instruction (taken or not taken). For example, when the processor sees code like this:

```bash
dec eax
jz .zero
# eax is not 0
...
zero:
# eax is 0
```

In the above example, the `jz` instruction is a branch. Modern CPU architectures try to predict the outcome of every branch to increase performance. This is called "Speculative Execution" that we discussed in [@sec:SpeculativeExec]. The processor will speculate that, for example, the branch will not be taken and will execute the code that corresponds to the situation when `eax is not 0`. However, if the guess is wrong, this is called "branch misprediction", and the CPU is required to undo all the speculative work that it has done recently. This typically involves a penalty between 10 and 20 clock cycles.

Linux `perf` users can check the number of branch mispredictions by running:

```bash
$ perf stat -e branches,branch-misses -- a.exe
   358209  branches
    14026  branch-misses #    3,92% of all branches        
# or simply do:
$ perf stat -- a.exe
```