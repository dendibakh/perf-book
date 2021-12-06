---
typora-root-url: ..\..\img
---

# Performance Analysis Approaches {#sec:sec_PerfApproaches}

When doing high-level optimization, it is usually easy to tell whether the performance was improved or not. When you write a better version of an algorithm, you expect to see a visible difference in the running time of the program. But also, there are situations when you see a change in execution time, but you have no clue where it's coming from. Time alone does not provide any insight into why that happens. In this case, we need more information about how our program executes. That's the situation when we need to do performance analysis to understand the underlying nature of the slowdown or speedup that we observe.

Both HW and SW track performance data while our program is running. In this context, by HW, we mean CPU, which executes the program, and by SW, we mean OS and all the tools enabled for analysis. Typically, the SW stack provides high-level metrics like time, number of context switches, and page-faults, while CPU is capable of observing cache-misses, branch mispredictions, etc. Depending on the problem we are trying to solve, some metrics would be more useful than others. So, it doesn't mean that HW metrics will always give us a more precise overview of the program execution. Some metrics, like the number of context-switches, for instance, cannot be provided by CPU. Performance analysis tools, like `Linux perf`, can consume data both from OS and CPU. 

We will use Linux `perf` extensively throughout the book as it is one of the most popular performance analysis tools. This tool is available on most Linux distributions, which makes it accessible for a wide range of users. Another reason why the author prefers showcasing Linux `perf` is that it is open-sourced, which allows us to see the mechanics of what is going on in a typical profiling tool. This is especially useful for learning concepts presented in this book because GUI-based tools, like Intel® VTune™ Profiler, tend to hide all the complexity. More information about Linux `perf` is available on its [wiki page](https://perf.wiki.kernel.org/index.php/Main_Page)[^1].

In this chapter, we will introduce some of the most popular performance analysis techniques: Code Instrumentation, Tracing, Characterization, and Sampling. We also discuss static performance analysis techniques and compiler optimization reports which do not involve running the actual application.

[^1]: Linux perf wiki - [https://perf.wiki.kernel.org/index.php/Main_Page](https://perf.wiki.kernel.org/index.php/Main_Page).
