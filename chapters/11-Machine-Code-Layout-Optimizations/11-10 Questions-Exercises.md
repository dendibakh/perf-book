## Questions and Exercises {.unlisted .unnumbered}

\markright{Questions and Exercises}

1. Solve `perf-ninja::pgo` lab assignment.
2. Experiment with using Huge Pages for the code section. Take a large application (access to source code is a plus but not necessary), with a binary size of more than 100MB. Try to remap its code section onto huge pages using one of the methods described in [@sec:FeTLB]. Observe any changes in performance, huge page allocation in `/proc/meminfo`, and CPU performance counters that measure ITLB loads and misses.
3. Suppose you have a code that has a large C++ switch statement in a loop. You instrumented the code and figured out that one particular case in a switch statement is used 70% of the time. The other 40 cases are used <3% of the time each and the rest 20 cases never happen. What will you do to optimize the performance of that switch/loop?
4. Run the application that you're working with daily. Apply PGO, llvm-bolt, or Propeller. Compare "before" and "after" profiles to understand where the speedups are coming from.
