## Chapter Summary {.unlisted .unnumbered}

\markright{Summary}

* We gave a quick overview of the most popular tools available on three major platforms: Linux, Windows, and MacOS. Depending on the CPU vendor, the choice of a profiling tool will vary. For systems with an Intel processor we recommend using VTune; for systems with an AMD processor use uProf; on Apple platforms use Xcode Instruments. 
* Linux perf is probably the most frequently used profiling tool on Linux. It has support for processors from all major CPU vendors. It doesn't have a graphical interface. However, some tools can visualize `perf`'s profiling data.
* We also discussed Windows Event Tracing (ETW), which is designed to observe software dynamics in a running system. Linux has a similar tool called [KUtrace](https://github.com/dicksites/KUtrace),[^1] which we do not cover in the book.
* There are hybrid profilers that combine techniques like code instrumentation, sampling, and tracing. This takes the best out of these approaches and allows users to get very detailed information on a specific piece of code. In this chapter, we looked at Tracy, which is quite popular among game developers.
* Memory profilers provide information about memory usage, heap allocations, memory footprint, and other metrics. Memory profiling helps you understand how an application uses memory over time.
* Continuous profiling tools have already become an essential part of monitoring performance in production environments. They collect system-wide performance metrics with call stacks for days, weeks, or even months. Such tools make it easier to spot the point in time when a performance change occurred and determine the root cause of an issue.

[^1]: KUtrace - [https://github.com/dicksites/KUtrace](https://github.com/dicksites/KUtrace)

\sectionbreak
