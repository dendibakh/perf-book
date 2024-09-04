## Chapter Summary {.unlisted .unnumbered}

\markright{Summary}

* Modern systems have non-deterministic performance. Eliminating non-determinism in a system is helpful for well-defined, stable performance tests, e.g., microbenchmarks.
* Measuring performance in production is required to assess how users perceive responsiveness of your services. However, this requires dealing with noisy environments and using statistical methods for analyzing results. 
* It is beneficial to employ an automated performance tracking system to prevent performance regressions from leaking into production software. Such CI systems are supposed to run automated performance tests, visualize results, and alert on discovered performance anomalies.
* Visualizing performance distributions helps comparing performance results. It is a safe way of presenting performance results to a wide audience.
* To benchmark execution time, engineers can use two different timers: the system-wide high-resolution timer and the Time Stamp Counter. The former is suitable for measuring events whose duration is more than a microsecond. The latter can be used for measuring short events with high accuracy.
* Microbenchmarks are good for quick experiments, but you should always verify your ideas on a real application in practical conditions. Make sure that you are benchmarking the right code by checking performance profiles.

\sectionbreak



