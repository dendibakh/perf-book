## Questions and Exercises {.unlisted .unnumbered}

\markright{Questions and Exercises}

1. Solve `perf-ninja::pgo` and `perf-ninja::lto` lab assignments.
2. Experiment with using Huge Pages for the code section. Take a large application (access to source code is a plus but not necessary), with a binary size of more than 100MB. Try to remap its code section onto huge pages using one of the methods described in [@sec:FeTLB]. Observe any changes in performance, huge page allocation in `/proc/meminfo`, and CPU performance counters that measure ITLB loads and misses.
3. Run the application that you're working with daily. Apply PGO, llvm-bolt, or Propeller and check the result. Compare "before" and "after" profiles to understand where the speedups are coming from.
