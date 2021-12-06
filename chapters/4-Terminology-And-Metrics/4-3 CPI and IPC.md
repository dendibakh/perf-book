---
typora-root-url: ..\..\img
---

## CPI & IPC {#sec:IPC}

Those are two very important metrics that stand for:

* Cycles Per Instruction (CPI) - how many cycles it took to retire one instruction on average.
* Instructions Per Cycle (IPC) - how many instructions were retired per one cycle on average.

$$
IPC = \frac{INST\_RETIRED.ANY}{CPU\_CLK\_UNHALTED.THREAD}
$$

$$
CPI = \frac{1}{IPC},
$$

where `INST_RETIRED.ANY` PMC counts the number of retired instructions, `CPU_CLK_UNHALTED.THREAD` counts the number of core cycles while the thread is not in a halt state.

There are many types of analysis that can be done based on those metrics. It is useful for both evaluating HW and SW efficiency. HW engineers use this metric to compare CPU generations and CPUs from different vendors. SW engineers look at IPC and CPI when they optimize their application. Universally, we want to have low CPI and high IPC. Linux `perf` users can get to know IPC for their workload by running:

```bash
$ perf stat -e cycles,instructions -- a.exe
  2369632  cycles                               
  1725916  instructions  #    0,73  insn per cycle
# or just simply do:
$ perf stat ./a.exe
```