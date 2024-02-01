## Case Study: Measuring Code Footprint {#sec:CodeFootprint}

[TODO]: define hot and non-cold code; maybe get rid of non-cold; also there is warm and cold code with a threshold.

As we mentioned a couple of times in this chapter, code layout optimizations are most impactful on applications with large amounts of code. The best way to clarify the uncertainty about the size of the hot code in your program is to measure its *code footprint*, which we define as the number of bytes/cache lines/pages with machine instructions the program touches during its execution.

A large code footprint by itself doesn't necessarily negatively impact performance. Code footprint is not a decisive metric, and it doesn't immediately tell you if there is a problem. Nevertheless, it has proven to be useful as an additional data point in performance analysis. In conjunction with TMA's `Frontend_Bound`, L1-instruction cache miss rate, and other metrics, it may strengthen the argument for investing time in optimizing the machine code layout of your application.

Currently, there are very few tools available that can reliably measure code footprint. In this case study, we will demonstrate [perf-tools](https://github.com/aayasin/perf-tools),[^1] an open-source collection of profiling tools built on top of Linux `perf`. To estimate[^2] code footprint, `perf-tools` leverages Intel's LBR (see [@sec:lbr]), so it currently doesn't work on AMD- or ARM-based systems. Below is a sample command to collect the code footprint data:

```
$ perf-tools/do.py profile --profile-mask 100 -a <your benchmark>
```

, where `--profile-mask 100` initiates LBR sampling, and `-a` enables you to specify a program to run. This command will collect code footprint along with various other data. We don't show the output of the tool, curious readers are welcome to try it out for themselves.

We took a set of four benchmarks: Clang C++ compilation, Blender ray tracing, Cloverleaf hydrodynamics, and Stockfish chess engine; these workloads should be already familiar to you from [@sec:PerfMetricsCaseStudy] where we analyzed their performance characteristics. We ran them on one of Intel's Alderlake-based processors using the same commands we used in [@sec:PerfMetricsCaseStudy]. As expected, the code footprint numbers obtained by running the same benchmarks on a Skylake-based machine are very similar to those from Alderlake run. Code footprint depends on the program and input data, and not on characteristics of a particular machine, so results should look similar across architectures.

Results for each of the four benchmarks are presented in Table @tbl:code_footprint. The binary and `.text` sizes were obtained with a standard Linux `readelf` utility, while other metrics were collected with `perf-tools`. If an instruction memory location was hit at least once, the tool considers it as "non-cold", thus, `non-cold code footprint [KB]` is the number of kilobytes with machine instructions that a program touched. The metric `non-cold code 4KB-pages` tells us the number of non-cold 4KB-pages with machine instructions that a program touched. Together they help us to understand how dense or sparse those non-cold memory locations are. It will become clear once we dig into the numbers. Finally, we also present Frontend Bound percentages, a metric that should be already familiar to you from [@sec:TMA] about TMA.

-------------------------------------------------------------------------------
Metric                               Clang17   Blender   CloverLeaf   Stockfish      
                                 compilation                                
------------------------------- ------------ --------- ------------ -----------
Binary size [KB]                      113844    223914          672       39583

`.text` size [KB]                      67309    133009          598         238

non-cold code footprint [KB]            5042       313          104          99

non-cold code 4KB-pages                 6614       546          104          61

Frontend Bound, Alderlake-P [%]         52.3      29.4          5.3        25.8
-------------------------------------------------------------------------------

Table: Code footprint of the benchmarks used in the case study. {#tbl:code_footprint}

Let's first look at the binary and `.text` sizes. CloverLeaf is a tiny application compared to Clang17 and Blender; Stockfish embeds the neural network file which accounts for the largest part of the binary, but its code section is relatively small; Clang17 and Blender have gigantic code bases. The `.text size` metric is the upper bound for our applications, i.e. we assume[^3] the code footprint should not exceed `.text` size.

A few interesting observations can be made by analyzing the code footprint data. First, even though the Blender `.text` section is very large, less than 1% of Blender's code is non-cold: 313 KB out of 133 MB. So, just because a binary size is large, doesn't mean the application suffers from CPU front-end bottlenecks. It's the amount of hot code that matters. For other benchmarks this ratio is higher: Clang17 7.5%, CloverLeaf 17.4%, Stockfish 41.6%. In absolute numbers, Clang17 compilation touches an order of magnitude more bytes with machine instructions than the other three applications.

Second, let's examine the `non-cold code 4KB-pages` row in the table. For Clang17, non-cold 5042 KB are spread over 6614 4KB pages, which gives us `5042 / (6614 * 4) = 19%` page utilization. This metric tells us how dense/sparse the hot parts of the code are. The closer each hot cache line is located to another hot cache line, the fewer pages are required to store the hot code. The higher the page utilization the better. Basic block placement and function reordering that we discussed earlier in this chapter are perfect examples of a transformation that improves page utilization. For other benchmarks, the ratios are: Blender 14%, CloverLeaf 25%, and Stockfish 41%. 

Now that we quantified the code footprints of the four applications, it's tempting to think about the size of L1-instruction and L2 caches and whether the hot code fits or not. On our Alderlake-based machine, the L1-I cache is only 32 KB, which is not enough to fully cover any of the benchmarks that we've analyzed. But remember, at the beginning of this section we said that a large code footprint doesn't immediately point to a problem. Yes, a large codebase puts more pressure on the CPU front-end, but an instruction access pattern is also crucial for performance. The same locality principles as for data accesses apply. That's why we accompanied it with the Frontend Bound metric from Topdown analysis. 

For Clang17, the 5 MB of non-cold code causes a huge 52.3% Frontend Bound performance bottleneck: more than half of the cycles are wasted waiting for instructions. From all the presented benchmarks, it benefits the most from PGO-type optimizations. CloverLeaf doesn't suffer from inefficient instruction fetch; 75% of its branches are backward jumps, which suggests that those could be relatively small loops executed over and over again. Stockfish, while having roughly the same non-cold code footprint as CloverLeaf, poses a far greater challenge for the CPU Front-end (25.8%). It has a lot more indirect jumps and function calls. Finally, Blender has even more indirect jumps and calls than Stockfish. We stop our analysis at this point as further investigations are outside the scope of this case study. For readers who are interested in continuing the analysis, we suggest drilling down into the Frontend Bound category according to the TMA methodology and looking at metrics such as `ICache_Misses`, `ITLB_Misses`, `DSB coverage`, and others.

Another useful tool to study the code footprint is [llvm-bolt-heatmap](https://github.com/llvm/llvm-project/blob/main/bolt/docs/Heatmaps.md)[^4], which is a part of llvm's BOLT project. This tool can produce code heatmaps that give a fine-grained understanding of the code layout in your application. Its primary uses are 1) evaluating whether the original code layout is compact or not and whether it can be optimized, 2) ensuring that optimized code layout is compact under real load.

[^1]: perf-tools - [https://github.com/aayasin/perf-tools](https://github.com/aayasin/perf-tools)
[^2]: The code footprint data collected by `perf-tools` is not exact since it is based on sampling LBR records. Other tools like Intel's `sde -footprint`, unfortunately, don't provide code footprint. However, it is not hard to write a PIN-based tool yourself that will measure the exact code footprint.
[^3]: It is not always true: an application itself may be tiny, but call into multiple other dynamically linked libraries, or it may make heavy use of kernel code.
[^4]: llvm-bolt-heatmap - [https://github.com/llvm/llvm-project/blob/main/bolt/docs/Heatmaps.md](https://github.com/llvm/llvm-project/blob/main/bolt/docs/Heatmaps.md)