

## Chapter Summary {.unlisted .unnumbered}

* Debugging performance issues is usually harder than debugging functional bugs due to measurement instability.
* You cannot stop optimizing unless you set a particular goal. To know if you reached the desired goal, you need to come up with meaningful definitions and metrics for how you will measure that. Depending on what you care about, it could be throughput, latency, operations per second (roofline performance), etc. 
* Modern systems have non-deterministic performance. Eliminating non-determinism in a system is helpful for well-defined, stable performance tests, e.g., microbenchmarks. Measuring performance in production deployment requires dealing with a noisy environment by using statistical methods for analyzing results.
* More and more often, vendors of large distributed SW choose to profile and monitor performance directly on production systems, which requires using only light-weight profiling techniques.
* It is very beneficial to employ an automated statistical performance tracking system for preventing performance regressions from leaking into production software. Such CI systems are supposed to run automated performance tests, visualize results, and alert on discovered perfomance anomalies.
* Visualizing performance distributions also may help discover performance anomalies. It is a safe way of presenting performance results to a wide audience.
* Statistical relationship between performance distributions is identified using Hypothesis Testing methods. Once it's determined that the difference is statistically significant, then the speedup can be calculated as a ratio between the means or geometric means.
* It's OK to discard cold runs to ensure that everything is running hot, but do not deliberately discard unwanted data. If you decide to discard some samples, do it uniformly for all distributions. 
* To benchmark execution time, engineers can use two different timers, which all the modern platforms provide. The system-wide high-resolution timer is suitable for measuring events whose duration is more than a microsecond. For measuring short events with high accuracy, use Time Stamp Counter.
* Microbenchmarks are good for proving something quickly, but you should always verify your ideas on a real application in practical conditions. Make sure that you are benchmarking the meaningful code by checking performance profiles.

\sectionbreak



