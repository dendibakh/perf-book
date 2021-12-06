---
typora-root-url: ..\..\img
---

## Retired vs. Executed Instruction

Modern processors typically execute more instructions than the program flow requires. This happens because some of them are executed speculatively, as discussed in [@sec:SpeculativeExec]. For usual instructions, the CPU commits results once they are available, and all preceding instructions are already retired. But for instructions executed speculatively, the CPU keeps their results without immediately committing their results. When the speculation turns out to be correct, the CPU unblocks such instructions and proceeds as normal. But when it comes out that the speculation happens to be wrong, the CPU throws away all the changes done by speculative instructions and does not retire them. So, an instruction processed by the CPU can be executed but not necessarily retired. Taking this into account, we can usually expect the number of executed instructions to be higher than the number of retired instructions.[^1]

There is a fixed performance counter (PMC) that collects the number of retired instructions. It can be easily obtained with Linux `perf` by running:

```bash
$ perf stat -e instructions ./a.exe
  2173414  instructions  #    0.80  insn per cycle 
# or just simply do:
$ perf stat ./a.exe
```

[^1]: Usually, a retired instruction has also gone through the execution stage, except those times when it does not require an execution unit. An example of it can be "MOV elimination" and "zero idiom". Read more on easyperf blog: [https://easyperf.net/blog/2018/04/22/What-optimizations-you-can-expect-from-CPU](https://easyperf.net/blog/2018/04/22/What-optimizations-you-can-expect-from-CPU). So, theoretically, there could be a case when the number of retired instructions is higher than the number of executed instructions.
