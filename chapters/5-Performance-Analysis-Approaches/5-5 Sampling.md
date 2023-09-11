---
typora-root-url: ..\..\img
---

## Sampling {#sec:profiling}

Sampling is the most frequently used approach for doing performance analysis. People usually associate it with finding hotspots in the program. In general terms, sampling gives the answer to the question: which place in the code contributes to the greatest number of certain performance events. If we consider finding hotspots, the problem can be reformulated as which place in the code consumes the biggest amount of CPU cycles. People often use the term "Profiling" for what is technically called sampling. According to [Wikipedia](https://en.wikipedia.org/wiki/Profiling_(computer_programming))[^1], profiling is a much broader term and includes a wide variety of techniques to collect data, including interrupts, code instrumentation, and PMC.

It may come as a surprise, but the simplest sampling profiler one can imagine is a debugger. In fact, you can identify hotspots by a) run the program under the debugger, b) pause the program every 10 seconds, and c) record the place where it stopped. If you repeat b) and c) many times, you will build a collection of samples. The line of code where you stopped the most will be the hottest place in the program. [^6] Of course, this is an oversimplified description of how real profiling tools work. Modern profilers are capable of collecting thousands of samples per second, which gives a pretty accurate estimate about the hottest places in a benchmark. 

As in the example with a debugger, the execution of the analyzed program is interrupted every time a new sample is captured. At the time of interrupt, the profiler collects the snapshot of the program state, which constitutes one sample. Information collected for every sample may include an instruction address that was executed at the time of interrupt, register state, call stack (see [@sec:secCollectCallStacks]), etc. Collected samples are stored in data collection files, which can be further used to display a call graph, the most time-consuming parts of the program, and control flow for statistically important code sections.

### User-Mode And Hardware Event-based Sampling

Sampling can be performed in 2 different modes, using user-mode or HW event-based sampling (EBS). User-mode sampling is a pure SW approach that embeds an agent library into the profiled application. The agent sets up the OS timer for each thread in the application. Upon timer expiration, the application receives the `SIGPROF` signal that is handled by the collector. EBS uses hardware PMCs to trigger interrupts. In particular, the counter overflow feature of the PMU is used, which we will discuss in the next section.[@IntelVTuneGuide]

User-mode sampling can only be used to identify hotspots, while EBS can be used for additional analysis types that involve PMCs, e.g., sampling on cache-misses, TMA (see [@sec:TMA]), etc.

User-mode sampling incurs more runtime overhead than EBS. The average overhead of the user-mode sampling is about 5% when sampling is using the default interval of 10ms. The average overhead of event-based sampling is about 2% on a 1ms sampling interval. Typically, EBS is more accurate since it allows collecting samples with higher frequency. However, user-mode sampling generates much fewer data to analyze, and it takes less time to process it. 

### Finding Hotspots

In this section, we will discuss the scenario of using PMCs with EBS. Figure @fig:Sampling illustrates the counter overflow feature of the PMU, which is used to trigger performance monitoring interrupt (PMI). 

![Using performance counter for sampling](../../img/perf-analysis/SamplingFlow.png){#fig:Sampling width=70%}

In the beginning, we configure the event that we want to sample on. Identifying hotspots means knowing where the program spends most of the time. So sampling on cycles is very natural, and it is a default for many profiling tools. But it's not necessarily a strict rule; we can sample on any performance event we want. For example, if we would like to know the place where the program experiences the biggest number of L3-cache misses, we would sample on the corresponding event, i.e., `MEM_LOAD_RETIRED.L3_MISS`.

After preparations are done, we enable counting and let the benchmark go. We configured PMC to count cycles, so it will be incremented every cycle. Eventually, it will overflow. At the time the counter overflows, HW will raise PMI. The profiling tool is configured to capture PMIs and has an Interrupt Service Routine (ISR) for handling them. Inside this routine, we do multiple steps: first of all, we disable counting; after that, we record the instruction which was executed by the CPU at the time the counter overflowed; then, we reset the counter to `N` and resume the benchmark.

Now, let us go back to the value `N`. Using this value, we can control how frequently we want to get a new interrupt. Say we want a finer granularity and have one sample every 1 million instructions. To achieve this, we can set the counter to `-1` million so that it will overflow after every 1 million instructions. This value is usually referred to as the "sample after" value.

We repeat the process many times to build a sufficient collection of samples. If we later aggregate those samples, we could build a histogram of the hottest places in our program, like the one shown on the output from Linux `perf record/report` below. This gives us the breakdown of the overhead for functions of a program sorted in descending order (hotspots). Example of sampling [x264](https://openbenchmarking.org/test/pts/x264)[^7] benchmark from [Phoronix test suite](https://www.phoronix-test-suite.com/)[^8] is shown below:

```bash
$ perf record -- ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
$ perf report -n --stdio
# Samples: 364K of event 'cycles:ppp'
# Event count (approx.): 300110884245
# Overhead  Samples  Shared Object   Symbol
# ........  .......  .............   ........................................
#
     6.99%    25349    x264          [.] x264_8_me_search_ref
     6.70%    24294    x264          [.] get_ref_avx2
     6.50%    23397    x264          [.] refine_subpel
     5.20%    18590    x264          [.] x264_8_pixel_satd_8x8_internal_avx2
     4.69%    17272    x264          [.] x264_8_pixel_avg2_w16_sse2
     4.22%    15081    x264          [.] x264_8_pixel_avg2_w8_mmx2
     3.63%    13024    x264          [.] x264_8_mc_chroma_avx2
     3.21%    11827    x264          [.] x264_8_pixel_satd_16x8_internal_avx2
     2.25%     8192    x264          [.] rd_cost_mb
	 ...
```

We would then naturally want to know the hot piece of code inside every function that appears in the hotspot list. To see the profiling data for functions that were inlined as well as assembly code generated for a particular source code region requires the application being built with debug information (`-g` compiler flag). Users can reduce[^4] the amount of debugging information to just line numbers of the symbols as they appear in the source code by using the `-gline-tables-only` option. Tools like Linux `perf` that don't have rich graphic support, intermix source code with the generated assembly, as shown below:

```bash
# snippet of annotating source code of 'x264_8_me_search_ref' function
$ perf annotate x264_8_me_search_ref --stdio
Percent | Source code & Disassembly of x264 for cycles:ppp 
----------------------------------------------------------
  ...
        :                 bmx += square1[bcost&15][0]; <== source code
  1.43  : 4eb10d:  movsx  ecx,BYTE PTR [r8+rdx*2]      <== corresponding
                                                           machine code
        :                 bmy += square1[bcost&15][1];
  0.36  : 4eb112:  movsx  r12d,BYTE PTR [r8+rdx*2+0x1]
        :                 bmx += square1[bcost&15][0];
  0.63  : 4eb118:  add    DWORD PTR [rsp+0x38],ecx
        :                 bmy += square1[bcost&15][1];
  ...
```

Most profilers with Graphical User Interface (GUI), like Intel VTune Profiler, can show source code and associated assembly side-by-side, as shown in figure @fig:SourceCode_View. 

![Intel® VTune™ Profiler source code and assembly view for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](../../img/perf-analysis/Vtune_source_level.png){#fig:SourceCode_View width=90%}

### Collecting Call Stacks {#sec:secCollectCallStacks}

Often when sampling, we might encounter a situation when the hottest function in a program gets called by multiple callers. An example of such a scenario is shown on figure @fig:CallStacks. The output from the profiling tool might reveal that `foo` is one of the hottest functions in the program, but if it has multiple callers, we would like to know which one of them call `foo` the most number of times. It is a typical situation for applications that have library functions like `memcpy` or `sqrt` appear in the hotspots. To understand why a particular function appeared as a hotspot, we need to know which path in the Control Flow Graph (CFG) of the program caused it.

![Control Flow Graph: hot function "foo" has multiple callers.](../../img/perf-analysis/CallStacksCFG.png){#fig:CallStacks width=50%}

Analyzing the logic of all the callers of `foo` might be very time-consuming. We want to focus only on those callers that caused `foo` to appear as a hotspot. In other words, we want to know the hottest path in the CFG of a program. Profiling tools achieve this by capturing the call stack of the process along with other information at the time of collecting performance samples. Then, all collected stacks are grouped, allowing us to see the hottest path that led to a particular function.

Collecting call stacks in Linux `perf` is possible with three methods:

1.  Frame pointers (`perf record --call-graph fp`). Requires binary being built with `--fnoomit-frame-pointer`. Historically, frame pointer (`RBP`) was used for debugging since it allows us to get the call stack without popping all the arguments from the stack (stack unwinding). The frame pointer can tell the return address immediately. However, it consumes one register just for this purpose, so it was expensive. It is also used for profiling since it enables cheap stack unwinding.
2.  DWARF debug info (`perf record --call-graph dwarf`). Requires binary being built with DWARF debug information `-g` (`-gline-tables-only`).
3.  Intel Last Branch Record (LBR) Hardware feature `perf record --call-graph lbr`. Not as deep call graph as the first two methods. See more information about LBR in the [@sec:lbr].

Below is the example of collecting call stacks in a program using Linux `perf`. By looking at the output, we know that 55% of the time `foo` was called from `func1`. We can clearly see the distribution of the overhead between callers of `foo` and can now focus our attention on the hottest edges in the CFG of the program.

```bash
$ perf record --call-graph lbr -- ./a.out
$ perf report -n --stdio --no-children
# Samples: 65K of event 'cycles:ppp'
# Event count (approx.): 61363317007
# Overhead       Samples  Command  Shared Object     Symbol
# ........  ............  .......  ................  ......................
    99.96%         65217  a.out    a.out             [.] foo
            |
             --99.96%--foo
                       |
                       |--55.52%--func1
                       |          main
                       |          __libc_start_main
                       |          _start
                       |
                       |--33.32%--func2
                       |          main
                       |          __libc_start_main
                       |          _start
                       |
                        --11.12%--func3
                                  main
                                  __libc_start_main
                                  _start
```

When using Intel Vtune Profiler, one can collect call stacks data by checking the corresponding "Collect stacks" box while configuring analysis[^2]. When using command-line interface specify `-knob enable-stack-collection=true` option.

\personal{The mechanism of collecting call stacks is very important to understand. I've seen some developers that are not familiar with the concept try to obtain this information by using a debugger. They do this by interrupting the execution of a program and analyze the call stack (like `backtrace` command in `gdb` debugger). Developers should allow profiling tools to do the job, which is much faster and gives more accurate data.}

[^1]: Profiling(wikipedia) - [https://en.wikipedia.org/wiki/Profiling_(computer_programming)](https://en.wikipedia.org/wiki/Profiling_(computer_programming)).
[^2]: See more details in [Intel® VTune™ Profiler User Guide](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top/analyze-performance/hardware-event-based-sampling-collection/hardware-event-based-sampling-collection-with-stacks.html).
[^4]: If a user doesn't need full debug experience, having line numbers is enough for profiling the application. There were cases when LLVM transformation passes incorrectly, treated the presence of debugging intrinsics, and made wrong transformations in the presence of debug information.
[^6]: This is an awkward way, though, and we don't recommend doing this. It's just to illustrate the concept.
[^7]: x264 benchmark - [https://openbenchmarking.org/test/pts/x264](https://openbenchmarking.org/test/pts/x264).
[^8]: Phoronix test suite - [https://www.phoronix-test-suite.com/](https://www.phoronix-test-suite.com/).
