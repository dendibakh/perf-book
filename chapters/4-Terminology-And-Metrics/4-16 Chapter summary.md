## Chapter Summary {.unlisted .unnumbered}

\markright{Summary}

* In this chapter, we introduced the basic metrics in performance analysis such as retired/executed instructions, CPU utilization, IPC/CPI, $\mu$ops, pipeline slots, core/reference clocks, cache misses and branch mispredictions. We showed how each of these metrics can be collected with Linux `perf`.
* For more advanced performance analysis, there are many derivative metrics that you can collect. For instance, cache misses per kilo instructions (MPKI), instructions per function call, branch, load, etc. (Ip*), ILP, MLP, and others. The case studies in this chapter show how you can get actionable insights from analyzing these metrics. 
* Be careful about drawing conclusions just by looking at the aggregate numbers. Don't fall into the trap of "Excel performance engineering", i.e., only collecting performance metrics and never looking at the code. Always seek a second source of data (e.g., performance profiles, discussed later) to verify your ideas.
* Memory bandwidth and latency are crucial factors in the performance of many production software packages nowadays, including AI, HPC, databases, and many general-purpose applications. Memory bandwidth depends on the DRAM speed (in MT/s) and the number of memory channels. Modern high-end server platforms have 8--12 memory channels and can reach up to 500 GB/s for the whole system and up to 50 GB/s in single-threaded mode. Memory latency nowadays doesn't change a lot, in fact, it is getting slightly worse with new DDR4 and DDR5 generations. The majority of modern systems fall in the range of 70--110 ns latency per memory access.

\sectionbreak



