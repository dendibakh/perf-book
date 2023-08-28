---
typora-root-url: ..\..\img
---

# CPU Features For Performance Analysis {#sec:sec4}

The ultimate goal of performance analysis is to identify the bottleneck and locate the place in the code that associates with it. Unfortunately, there are no predetermined steps to follow, so it can be approached in many different ways. 

Usually, profiling the application can give quick insights about the hotspots of the application. Sometimes it is everything developers need to do to fix performance inefficiencies. Especially high-level performance problems can often be revealed by profiling. For example, consider a situation when you profile an application with interest in a particular function. According to your mental model of the application, you expect that function to be cold. But when you open the profile, you see it consumes a lot of time and is called a large number of times. Based on that information, you can apply techniques like caching or memoization to reduce the number of calls to that function and expect to see significant performance gains.

However, when you have fixed all the major performance inefficiencies, but you still need to squeeze more performance from your application, basic information like the time spent in a particular function is not enough. Here is when you need additional support from the CPU to understand where the performance bottlenecks are. So, before using the information presented in this chapter, make sure that the application you are trying to optimize does not suffer from major performance flaws. Because if it does, using CPU performance monitoring features for low-level tuning doesn't make sense. It will likely steer you in the wrong direction, and instead of fixing real high-level performance problems, you will be tuning bad code, which is just a waste of time.

\personal{When I was starting with performance optimization work, I usually just profiled the app and tried to grasp through the hotspots of the benchmark, hoping to find something there. This often led me to random experiments with unrolling, vectorization, inlining, you name it. I’m not saying it’s always a losing strategy. Sometimes you can be lucky to get a big performance boost from random experiments. But usually, you need to have very good intuition and luck.}

Modern CPUs are constantly getting new features that enhance performance analysis in different ways. Using those features greatly simplifies finding low-level issues like cache-misses, branch mispredictions, etc. In this chapter, we will take a look at a few HW performance monitoring capabilities available on modern Intel CPUs. Most of them also have their counterparts in CPUs from other vendors like AMD, ARM, and others. Look for more details in the corresponding sections.

* Top-Down Microarchitecture Analysis Methodology (TMA) - a powerful technique for identifying ineffective usage of CPU microarchitecture by the program. It characterizes the bottleneck of the workload and allows locating the exact place in the source code where it occurs. It abstracts away intricacies of the CPU microarchitecture and is easy to use even for inexperienced developers.
* Last Branch Record (LBR) - a mechanism that continuously logs the most recent branch outcomes in parallel with executing the program. It is used for collecting call stacks, identify hot branches, calculating misprediction rates of individual branches, and more.
* Processor Event-Based Sampling (PEBS) - a feature that enhances sampling. Among its primary advantages are: lowering the overhead of sampling and providing "Precise Events" capability, which allows pinpointing exact instruction that caused a particular performance event.
* Intel Processor Traces (PT) - a facility to record and reconstruct the program execution with a timestamp on every instruction. Its main usages are postmortem analysis and root-causing performance glitches.

The Intel PT feature is covered in Appendix D. Intel PT was supposed to be an "end game" for performance analysis. With its low runtime overhead, it is a very powerful analysis feature. But it turns out to be not very popular among performance engineers. Partially because the support in the tools is not mature, partially because in many cases it is an overkill, and it's just easier to use a sampling profiler. Also, it produces a lot of data, which is not practical for long-running workloads.

The features mentioned above provide insights on the efficiency of a program from the CPU perspective. In the next chapter we will discuss how profiling tools leverage them to provide many different types of performance analysis.
