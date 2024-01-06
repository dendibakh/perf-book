---
typora-root-url: ..\..\img
---

## Chapter Summary {.unlisted .unnumbered}

* In this chapter, we introduced the basic metrics in performance analysis such as retired/executed instructions, CPU utilization, IPC/CPI, μops, pipeline slots, core/reference clocks, cache misses and branch mispredictions. We showed how each of these metrics can be collected with Linux perf.
* For more advanced performance analysis, there are many derivative metrics that one can collect. For instance, MPKI (misses per kilo instructions), Ip* (instructions per function call, branch, load, etc), ILP, MLP and others. The case study in this chapter shows how we can get actionable insights from analyzing these metrics. Although, be carefull about drawing conclusions just by looking at the aggregate numbers. Don't fall in the trap of "excel performance engineering", i.e. only collect performance metrics and never look at the code. Always seek for a second source of data (e.g. performance profiles, discussed later) that will confirm your hypothesis.
* Memory bandwidth and latency are crucial factors in performance of many production SW packages nowadays, including AI, HPC, databases, and many general-purpose applications. Memory bandwidth depends on the DRAM speed (in MT/s) and the number of memory channels. Modern high-end server platforms have 8-12 memory channels and can reach up to 500 GB/s for the whole system and up to 50 GB/s in single-threaded mode. Memory latency nowadays doesn't change a lot, in fact it is getting slightly worse with new DDR4 and DDR5 generations. Majority of systems fall in the range of 70-110 ns per memory access.

\sectionbreak



