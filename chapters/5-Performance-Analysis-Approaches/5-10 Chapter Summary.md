## Chapter Summary {#sec:secApproachesSummary .unlisted .unnumbered}

\markright{Summary}

* Latency and throughput are often the ultimate metrics of the program performance. When seeking ways to improve them, we need to get more detailed information on how the application executes. Both hardware and software provide data that can be used for performance monitoring.

* Code instrumentation enables us to track many things in a program but causes relatively large overhead both on the development and runtime side. While most developers are not in the habit of manually instrumenting their code, this approach is still relevant for automated processes, e.g., Profile-Guided Optimizations (PGO).

* Tracing is conceptually similar to instrumentation and is useful for exploring anomalies in a system. Tracing enables us to catch the entire sequence of events with timestamps attached to each event.

* Performance monitoring counters are a very important instrument of low-level performance analysis. They are generally used in two modes: "Counting" or "Sampling". The counting mode is primarily used for calculating various performance metrics. 

* Sampling skips most of a program's execution and takes just one sample that is supposed to represent the entire interval. Despite this, sampling usually yields precise enough distributions. The most well-known use case of sampling is finding hotspots in a program. Sampling is the most popular analysis approach since it doesn't require recompilation of a program and has very little runtime overhead.

* Generally, counting and sampling incur very low runtime overhead (usually below 2%). Counting gets more expensive once you start multiplexing between different events (5--15% overhead), while sampling gets more expensive with increasing sampling frequency [@Nowak2014TheOO]. User-mode sampling can be used for analyzing long-running workloads or when you don't need very accurate data.

* The Roofline Performance Model is a throughput-oriented performance model that is heavily used in the High Performance Computing (HPC) world. It visualizes the performance of an application against hardware limitations. The Roofline model helps to identify performance bottlenecks, guides software optimizations, and keeps track of optimization progress.

* There are tools that try to statically analyze the performance of code. Such tools simulate a piece of code instead of executing it. Many limitations and constraints apply to this approach, but you get a very detailed and low-level report in return.

* Compiler Optimization reports help to find missing compiler optimizations. These reports also guide developers when composing new performance experiments.

\sectionbreak
