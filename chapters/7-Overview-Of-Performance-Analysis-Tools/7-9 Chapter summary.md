## Chapter Summary {.unlisted .unnumbered}

* We gave a quick overview of the most popular tools available on three major platforms: Linux, Windows and MacOS. Depending on a CPU vendor, the choice of a profiling tool will vary. For systems with an Intel processor we recommend using Vtune, for systems with an AMD processor use uProf, on Apple platforms use Xcode Instruments. 

* Linux perf is probably the most frequently used profiling tool on Linux. It has support for processors from all major CPU vendors. It doesn't have a graphical interface, however, there are free tools that can visualize `perf` profiling data.

* We also discussed Windows Event Tracing (ETW), which is designed to observe SW dynamics in a running system. Linux has a similar tool called [KUtrace](https://github.com/dicksites/KUtrace)[^1], which we do not cover here.

* Also, there are hybrid profilers that combine techniques like code instrumentation, sampling and tracing. This takes the best out of these approaches and allows user to get a very detailed information on a specific piece of code. In this chapter we looked at Tracy, which is quite popular among game developers.

* Continuous profilers already become an essential tool for monitoring performance in production environments. They collect system-wide performance metrics with call stacks for days, weeks or even months. Such tools make it easier to spot the point of performance change and root cause an issue.

[^1]: KUtrace - [https://github.com/dicksites/KUtrace](https://github.com/dicksites/KUtrace)

\sectionbreak
