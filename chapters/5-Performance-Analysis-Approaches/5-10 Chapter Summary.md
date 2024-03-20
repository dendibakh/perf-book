---
typora-root-url: ..\..\img
---

## Chapter Summary {#sec:secApproachesSummary .unlisted .unnumbered}

* Latency and throughput are often the ultimate metrics of the program performance. When seeking ways to improve them, we need to get more detailed information on how the application executes. Both HW and SW provide data that can be used for performance monitoring.

* Code instrumentation enables us to track many things in the program but causes relatively large overhead both on the development and runtime side. While most developers are not in the habit of manually instrumenting their code, this approach is still relevant for automated processes, e.g., Profile-Guided Optimizations (PGO).

* Tracing is conceptually similar to instrumentation and is useful for exploring anomalies in a system. Tracing enables us to catch the entire sequence of events with timestamps attached to each event.

* Workload Characterization is a way to compare and group applications based on their runtime behavior. Once characterized, specific recipes could be followed to find optimization headrooms in the program. Profiling tools with marker APIs are useful for analyzing performance of a specific code region.

* Sampling skips most of a program's execution and takes just one sample that is supposed to represent the entire interval. Despite this, sampling usually yields precise enough distributions. The most well-known use case of sampling is finding hotspots in the code. Sampling is the most popular analysis approach since it doesn't require recompilation of the program and has very little runtime overhead.

* Generally, counting and sampling incur very low runtime overhead (usually below 2%). Counting gets more expensive once you start multiplexing between different events (5-15% overhead), sampling gets more expensive with increasing sampling frequency [@Nowak2014TheOO]. Consider using user-mode sampling for analyzing long-running workloads or when you don't need very accurate data.

* The Roofline Performance Model is a throughput-oriented performance model that is heavily used in the High Performance Computing (HPC) world. It visualizes the performance of an application against hardware limitations. Roofline model helps to identify performance bottlenecks, guides software optimizations, and keeps track of optimization progress.

* There are tools that try to statically analyze the performance of code. Such tools simulate a piece of code instead of executing it. Many limitations and constraints apply to this approach, but you get a very detailed and low-level report in return.

* Compiler Optimization reports help to find missing compiler optimizations. These reports also guide developers when composing new performance experiments.

\sectionbreak