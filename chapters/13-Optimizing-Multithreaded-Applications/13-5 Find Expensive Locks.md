### Find Expensive Locks with Intel VTune

[TODO]: Update/rework this section

Intel VTune Profiler has a dedicated type of analysis for multithreaded applications called [Threading Analysis](https://software.intel.com/en-us/vtune-help-threading-analysis). Its summary window (see Figure @fig:MT_VtuneThreadSummary) displays statistics on the overall application execution, identifying all the metrics we described in [@sec:secMT_metrics]. From the Effective CPU Utilization histogram, we can learn several interesting facts about the captured application behavior. First, on average, only 5 HW threads (logical cores on the diagram) were utilized at the same time. Second, it was very rare for all 8 HW threads to be active at the same time.

![Intel VTune Profiler Threading Analysis summary for [x264](https://openbenchmarking.org/test/pts/x264) benchmark from [Phoronix test suite](https://www.phoronix-test-suite.com/).](../../img/mt-perf/VtuneThreadingSummary.png){#fig:MT_VtuneThreadSummary width=80%}

### Find Expensive Locks {.unlisted .unnumbered}

Next, the workflow suggests that we identify the most contended synchronization objects. Figure @fig:MT_VtuneThreadObjects shows the list of such objects. We can see that `__pthread_cond_wait` definitely stands out, but since we might have dozens of conditional variables in the program, we need to know which one is the reason for poor CPU utilization.

![Intel VTune Profiler Threading Analysis showing the most contended synchronization objects for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingWaitingObjects.png){#fig:MT_VtuneThreadObjects width=90%}

To find out, we can simply click on `__pthread_cond_wait`, which will get us to the Bottom-Up view that is shown on Figure @fig:MT_VtuneLockCallStack. We can see the most frequent path (47% of wait time) that leads to threads waiting on conditional variable: `__pthread_cond_wait <- x264_8_frame_cond_wait <- mb_analyse_init`.

![Intel VTune Profiler Threading Analysis showing the call stack for the most contended conditional variable in [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingLockCallStack.png){#fig:MT_VtuneLockCallStack width=90%}

We can next jump into the source code of `x264_8_frame_cond_wait` by double-clicking on the corresponding row in the analysis (see Figure @fig:MT_VtuneLockSourceCode). Next, we can study the reason behind the lock and possible ways to make thread communication in this place more efficient. [^15]

![Source code view for x264_8_frame_cond_wait function in [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingLockSourceCode.png){#fig:MT_VtuneLockSourceCode width=90%}

### Platform View {.unlisted .unnumbered}

Another very useful feature of Intel VTune Profiler is Platform View (see Figure @fig:MT_VtunePlatform), which allows us to observe what each thread was doing in any given moment of program execution. This is very helpful for understanding the behavior of the application and finding potential performance headrooms. For example, we can see that during the time interval from 1s to 3s, only two threads were consistently utilizing ~100% of the corresponding CPU core (threads with TID 7675 and 7678). CPU utilization of other threads was bursty during that time interval. 

![Vtune Platform view for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/mt-perf/VtuneThreadingPlatformView.png){#fig:MT_VtunePlatform width=90%}

Platform View also has zooming and filtering capabilities. This allows us to understand what each thread was executing during a specified time frame. To see this, select the range on the timeline, right-click and choose Zoom In and Filter In by Selection. Intel VTune Profiler will display functions or sync objects used during this time range.

### Find Expensive Locks with Linux Perf

Linux `perf` tool profiles all the threads that the application might spawn. It has the `-s` option, which records per-thread event counts. Using this option, at the end of the report, `perf` lists all the thread IDs along with the number of samples collected for each of them:

```bash
$ perf record -s ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
$ perf report -n -T
...
#  PID   TID   cycles:ppp
  6966  6976  41570283106
  6966  6971  25991235047
  6966  6969  20251062678
  6966  6975  17598710694
  6966  6970  27688808973
  6966  6972  23739208014
  6966  6973  20901059568
  6966  6968  18508542853
  6966  6967     48399587
  6966  6966   2464885318
```

To filter samples for a particular software thread, one can use the `--tid` option:

```bash
$ perf report -T --tid 6976 -n
# Overhead  Samples  Shared Object  Symbol
# ........  .......  .............  ...................................
     7.17%   19877       x264       get_ref_avx2
     7.06%   19078       x264       x264_8_me_search_ref
     6.34%   18367       x264       refine_subpel
     5.34%   15690       x264       x264_8_pixel_satd_8x8_internal_avx2
     4.55%   11703       x264       x264_8_pixel_avg2_w16_sse2
     3.83%   11646       x264       x264_8_pixel_avg2_w8_mmx2
```

Linux `perf` also automatically provides some of the metrics we discussed in [@sec:secMT_metrics]: 

```bash
$ perf stat ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
         86,720.71 msec task-clock        #    5.701 CPUs utilized
            28,386      context-switches  #    0.327 K/sec
             7,375      cpu-migrations    #    0.085 K/sec
            38,174      page-faults       #    0.440 K/sec
   299,884,445,581      cycles            #    3.458 GHz
   436,045,473,289      instructions      #    1.45  insn per cycle
    32,281,697,229      branches          #  372.249 M/sec
       971,433,345      branch-misses     #    3.01% of all branches
```

### Find Expensive Locks {.unlisted .unnumbered}

To find the most contended synchronization objects with Linux `perf`, one needs to sample on scheduler context switches (`sched:sched_switch`), which is a kernel event and thus requires root access:

```bash
$ sudo perf record -s -e sched:sched_switch -g --call-graph dwarf -- ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
$ sudo perf report -n --stdio -T --sort=overhead,prev_comm,prev_pid --no-call-graph -F overhead,sample
# Samples: 27K of event 'sched:sched_switch'
# Event count (approx.): 27327
# Overhead       Samples         prev_comm    prev_pid
# ........  ............  ................  ..........
    15.43%          4217              x264        2973
    14.71%          4019              x264        2972
    13.35%          3647              x264        2976
    11.37%          3107              x264        2975
    10.67%          2916              x264        2970
    10.41%          2844              x264        2971
     9.69%          2649              x264        2974
     6.87%          1876              x264        2969
     4.10%          1120              x264        2967
     2.66%           727              x264        2968
     0.75%           205              x264        2977
```

The output above shows which threads were switched out from the execution most frequently. Notice, we also collect call stacks (`--call-graph dwarf`, see [@sec:secCollectCallStacks]) because we need it for analyzing paths that lead to the expensive synchronization events:

```bash
$ sudo perf report -n --stdio -T --sort=overhead,symbol -F overhead,sample -G
# Overhead       Samples  Symbol
# ........  ............  ...........................................
   100.00%         27327  [k] __sched_text_start                     
   |
   |--95.25%--0xffffffffffffffff
   |  |
   |  |--86.23%--x264_8_macroblock_analyse
   |  |  |
   |  |   --84.50%--mb_analyse_init (inlined)
   |  |     |
   |  |      --84.39%--x264_8_frame_cond_wait
   |  |        |
   |  |         --84.11%--__pthread_cond_wait (inlined)
   |  |                   __pthread_cond_wait_common (inlined)
   |  |                   |
   |  |                    --83.88%--futex_wait_cancelable (inlined)
   |  |                              entry_SYSCALL_64
   |  |                              do_syscall_64
   |  |                              __x64_sys_futex
   |  |                              do_futex
   |  |                              futex_wait
   |  |                              futex_wait_queue_me
   |  |                              schedule
   |  |                              __sched_text_start
   ...
```

The listing above shows the most frequent path that leads to waiting on a conditional variable (`__pthread_cond_wait`) and later context switch. This path is `x264_8_macroblock_analyse -> mb_analyse_init -> x264_8_frame_cond_wait`. From this output, we can learn that 84% of all context switches were caused by threads waiting on a conditional variable inside `x264_8_frame_cond_wait`. 

[^15]: I don’t claim that it will be necessary an easy road, and there is no guarantee that you will find a way to make it better.