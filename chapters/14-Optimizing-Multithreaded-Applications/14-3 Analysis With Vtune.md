---
typora-root-url: ..\..\img
---

## Analysis with Intel VTune Profiler

Intel VTune Profiler has a dedicated type of analysis for multithreaded applications called [Threading Analysis](https://software.intel.com/en-us/vtune-help-threading-analysis). Its summary window (see Figure @fig:MT_VtuneThreadSummary) displays statistics on the overall application execution, identifying all the metrics we described in [@sec:secMT_metrics]. From the Effective CPU Utilization histogram, we can learn several interesting facts about the captured application behavior. First, on average, only 5 HW threads (logical cores on the diagram) were utilized at the same time. Second, it was very rare for all 8 HW threads to be active at the same time.

![Intel VTune Profiler Threading Analysis summary for [x264](https://openbenchmarking.org/test/pts/x264) benchmark from [Phoronix test suite](https://www.phoronix-test-suite.com/).](../../img/mt-perf/VtuneThreadingSummary.png){#fig:MT_VtuneThreadSummary width=80%}

### Find Expensive Locks

Next, the workflow suggests that we identify the most contended synchronization objects. Figure @fig:MT_VtuneThreadObjects shows the list of such objects. We can see that `__pthread_cond_wait` definitely stands out, but since we might have dozens of conditional variables in the program, we need to know which one is the reason for poor CPU utilization.

![Intel VTune Profiler Threading Analysis showing the most contended synchronization objects for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingWaitingObjects.png){#fig:MT_VtuneThreadObjects width=90%}

To find out, we can simply click on `__pthread_cond_wait`, which will get us to the Bottom-Up view that is shown on Figure @fig:MT_VtuneLockCallStack. We can see the most frequent path (47% of wait time) that leads to threads waiting on conditional variable: `__pthread_cond_wait <- x264_8_frame_cond_wait <- mb_analyse_init`.

![Intel VTune Profiler Threading Analysis showing the call stack for the most contended conditional variable in [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingLockCallStack.png){#fig:MT_VtuneLockCallStack width=90%}

We can next jump into the source code of `x264_8_frame_cond_wait` by double-clicking on the corresponding row in the analysis (see Figure @fig:MT_VtuneLockSourceCode). Next, we can study the reason behind the lock and possible ways to make thread communication in this place more efficient. [^15]

![Source code view for x264_8_frame_cond_wait function in [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingLockSourceCode.png){#fig:MT_VtuneLockSourceCode width=90%}

### Platform View

Another very useful feature of Intel VTune Profiler is Platform View (see Figure @fig:MT_VtunePlatform), which allows us to observe what each thread was doing in any given moment of program execution. This is very helpful for understanding the behavior of the application and finding potential performance headrooms. For example, we can see that during the time interval from 1s to 3s, only two threads were consistently utilizing ~100% of the corresponding CPU core (threads with TID 7675 and 7678). CPU utilization of other threads was bursty during that time interval. 

![Vtune Platform view for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingPlatformView.png){#fig:MT_VtunePlatform width=90%}

Platform View also has zooming and filtering capabilities. This allows us to understand what each thread was executing during a specified time frame. To see this, select the range on the timeline, right-click and choose Zoom In and Filter In by Selection. Intel VTune Profiler will display functions or sync objects used during this time range.

[^15]: I don’t claim that it will be necessary an easy road, and there is no guarantee that you will find a way to make it better.
