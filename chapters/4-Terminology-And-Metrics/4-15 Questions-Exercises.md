## Questions and Exercises {.unlisted .unnumbered}

1. What is the difference between CPU core clock and reference clock?
2. What is the difference between retired and executed instruction?
3. Take a look at the `DRAM BW Use` formula in the table {@tbl:perf_metrics}. Why do you think there is a constant `64`?
4. Measure bandwidth and latency of the cache hierarchy and memory on the machine you use for development/benchmarking using MLC, stream or other tools.
5. Run the application that you're working with on a daily basis. Collect performance metrics. Does anything surprises you?
6. Imagine you are the owner of four applications we benchmarked in the case study. The management of your company asked you to build a small computing farm for each of those applications. A spending budget you were given is tight but enough to buy 2-3 machines to run each workload, so 8-12 machines in total. Look at the performance characteristics for the four applications once again and write down which computer parts (CPU, memory, discrete GPU if needed) you would buy for each of those workloads. Try to describe it in as much details as possible, search the web for exact components and their prices. What additional performance experiments you would run to guide your decision?