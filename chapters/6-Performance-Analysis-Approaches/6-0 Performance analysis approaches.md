---
typora-root-url: ..\..\img
---

# Performance Analysis Approaches {#sec:sec_PerfApproaches}

When doing high-level optimization, it is usually easy to tell whether the performance was improved or not. When you write a better version of an algorithm, you expect to see a visible difference in the running time of the program. But also, there are situations when you see a change in execution time, but you have no clue where it's coming from. Time alone does not provide any insight into why that happens. In this case, we need more information about how our program executes. That's the situation when we need to do performance analysis to understand the underlying nature of the slowdown or speedup that we observe.

[TODO]: elaborate on the idea: to solve a performance mystery, sometimes you just try different methods to gather clues. Once you have enough clues, you see if you can make a good explanation for the behavior you're observing.

Both HW and SW track performance data while our program is running. In this context, by HW, we mean CPU, which executes the program, and by SW, we mean OS and all the tools enabled for the analysis. Typically, the SW stack provides high-level metrics like time, number of context switches, and page-faults, while CPU monitors cache-misses, branch mispredictions, etc. Depending on the problem we are trying to solve, some metrics would be more useful than others. So, it doesn't mean that HW metrics will always give us a more precise overview of the program execution. Some metrics, like the number of context-switches, for instance, cannot be provided by CPU. Performance analysis tools, like `Linux perf`, can consume data both from OS and CPU. 

In this chapter, we will introduce some of the most popular performance analysis techniques: Code Instrumentation, Tracing, Characterization, and Sampling. We also discuss static performance analysis techniques and compiler optimization reports which do not involve running the actual application.