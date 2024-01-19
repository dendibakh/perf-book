### TMA On ARM Platforms

ARM CPU architects also have developed a TMA performance analysis methodology for their processors, which we will discuss next. ARM calls it "Topdown" in their documentation, so we will use their naming. At the time of writing this chapter (late 2023), Topdown is only supported on cores designed by ARM, e.g. Neoverse N1 and Neoverse V1, and their derivatives, e.g. Ampere Altra and AWS Graviton3. Refer to the list of major CPU microarchitectures in the end of this book if you need to refresh your memory on ARM chip families. Processors designed by Apple doesn't support the ARM Topdown performance analysis methodology yet.

ARM Neoverse V1 is the first CPU in the Neoverse family that supports a full set of level 1 Topdown metrics: `Bad Speculation`, `Frontend Bound`, `Backend Bound`, and `Retiring`. Future Neoverse cores are said to support further levels of TMA. At the time of writing, there are no analysis guides for Neoverse N2 and V2 cores. Prior to V1 cores, Neoverse N1 supported only two L1 categories: `Frontend Stalled Cycles` and `Backend Stalled Cycles`.

To demonstrate ARM's Topdown analysis on V1-based processor, we launched an AWS EC2 `m7g.metal` instance powered by the AWS Graviton3. Note that Topdown might not work on other non-metal instance types due to virtualization. We requested 64-bit ARM `Ubuntu 22.04 LTS` with `Linux kernel 6.2` managed by AWS. The provided `m7g.metal` instance had 64 vCPUs and 256 GB of RAM.

We apply the Topdown methodology to [AI Benchmark Alpha](https://ai-benchmark.com/alpha.html),[^1] which is an open source python library for evaluating AI performance of various hardware platforms, including CPUs, GPUs and TPUs. The benchmark relies on TensorFlow machine learning library to measure inference and training speed for key Deep Learning models. In total, AI Benchmark Alpha consists of 42 tests, including classification, image segmentation, text translation, and others.

ARM engineers have developed the [topdown-tool](https://learn.arm.com/install-guides/topdown-tool/)[^2] that we will use below. Similar to Intel's TMA, the ARM's methodology employs the "drill-down" concept, i.e. you first determine the high-level performance bottleneck and then drill down for a more nuanced root cause analysis. Here are the command we used:

```bash
$ topdown-tool --all-cpus -m Topdown_L1 -- python -c "from ai_benchmark import AIBenchmark; results = AIBenchmark(use_CPU=True).run()"
Stage 1 (Topdown metrics)
=========================
[Topdown Level 1]
Frontend Bound... 16.48% slots
Backend Bound.... 54.92% slots
Retiring......... 27.99% slots
Bad Speculation..  0.59% slots
```

where the `--all-cpus` option enables system-wide collection for all CPUs, and `-m Topdown_L1` collects Topdown Level 1 metrics. Everything that follows `--` is the command line to run the AI Benchmark Alpha suite.

From the output above, we conclude that the benchmark doesn't suffer from branch mispredictions. Also, without deeper understanding of the workloads involved, it's hard to say if the `Frontend Bound` of 16.5% is worth looking at, so we turn our attention to the `Backend Bound` metric, which is clearly the main source of stalled cycles. Neoverse V1-based chips don't have the second level breakdown, instead, the methodology suggests to further explore the problematic category by collecting a set of corresponding metrics. Here is how we drill down into the more detailed `Backend Bound` analysis:

```bash
$ topdown-tool --all-cpus -n BackendBound -- python -c "from ai_benchmark import AIBenchmark; results = AIBenchmark(use_CPU=True).run()"
Stage 1 (Topdown metrics)
=========================
[Topdown Level 1]
Backend Bound......................... 54.70% slots

Stage 2 (uarch metrics)
=======================
  [Data TLB Effectiveness]
  DTLB MPKI........................... 0.413 misses per 1,000 instructions
  L1 Data TLB MPKI.................... 3.779 misses per 1,000 instructions
  L2 Unified TLB MPKI................. 0.407 misses per 1,000 instructions
  DTLB Walk Ratio..................... 0.001 per TLB access
  L1 Data TLB Miss Ratio.............. 0.013 per TLB access
  L2 Unified TLB Miss Ratio........... 0.112 per TLB access

  [L1 Data Cache Effectiveness]
  L1D Cache MPKI...................... 13.114 misses per 1,000 instructions
  L1D Cache Miss Ratio................  0.046 per cache access

  [L2 Unified Cache Effectiveness]
  L2 Cache MPKI....................... 1.458 misses per 1,000 instructions
  L2 Cache Miss Ratio................. 0.027 per cache access

  [Last Level Cache Effectiveness]
  LL Cache Read MPKI.................. 2.505 misses per 1,000 instructions
  LL Cache Read Miss Ratio............ 0.219 per cache access
  LL Cache Read Hit Ratio............. 0.783 per cache access

  [Speculative Operation Mix]
  Load Operations Percentage.......... 25.36% operations
  Store Operations Percentage.........  2.54% operations
  Integer Operations Percentage....... 29.60% operations
  Advanced SIMD Operations Percentage. 10.93% operations
  Floating Point Operations Percentage  6.85% operations
  Branch Operations Percentage........ 10.04% operations
  Crypto Operations Percentage........  0.00% operations
```

[TODO]: why operation mix doesn't sum up to 100%?

In the command above, the option `-n BackendBound` collects all the metrics associated the `Backend Bound` category as well as its descendants. The description for every metric in the output is given in [@ARMNeoverseV1TopDown]. Note, that they are quite similar to what we have discussed in [@sec:PerfMetricsCaseStudy], so you may want to revisit it as well.

We don't have a goal of optimizing the benchmark, rather we want to characterize performance bottlenecks. However, if given such a task, here is how our analysis could continue. There is substantial number of `L1 Data TLB` misses (3.8 MPKI), but then 90% of those misses hit in L2 TLB (see `L2 Unified TLB Miss Ratio`). All in all, only 0.1% of all TLB misses result in a page table walk (see `DTLB Walk Ratio`), which suggests that it is not our primary concern, although a quick experiment that utilizes huge pages is still worth it.

Looking at the `L1/L2/LL Cache Effectiveness` metrics, we can spot a potential problem with data cache misses. One in ~22 accesses to L1D cache result in a miss (see `L1D Cache Miss Ratio`), which is tolerable but still expensive. For L2, this number is one in 37 (see `L2 Cache Miss Ratio`), which is much better. However for LLC, the `LL Cache Read Miss Ratio` is unsatisfying: every 4th access results in a miss. Since this is an AI benchmark, where the bulk of time could be spent in matrix multiplication, code transformations like loop blocking may help (see [@sec:LoopOpts]).

[TODO]: AI algorithms are known for being "memory hungry", however, this data doesn't give insights into the memory bandwidth consumption.

The final category gives the operation mix, which can be useful in certain scenarios. In our case, we should be concerned by the low percentage of SIMD operations, especially given that the highly optimized `Tensorflow` and `numpy` libraries are used. In contrast, the percentage of integer operations and branches seem too high. Branches could be coming from the Python interpreter or excessive function calls. While high percentage of integer operations could be caused by lack of vectorization, or thread synchronization. [@ARMNeoverseV1TopDown] gives an example of discovering a vectorization opportunity using data from the `Speculative Operation Mix` category. 

In our case study, we ran the benchmark two times, however, in practice, one run is usually sufficient. Running the `topdown-tool` without options will collect all the available metrics using a single run. Also, the `-s combined` option will group the metrics by the L1 category, and output data in a format similar to `Intel Vtune`, `toplev`, and other tools. The only practical reason for making multiple runs is when a workload has a bursty behavior with very short phases that have different performance characteristics. In such a scenario, you would like to avoid event multiplexing (see [@sec:secMultiplex]) and improve collection accuracy by running the workload multiple times. 

The AI Benchmark Alpha has various tests that could exhibit different performance characteristics. The output presented above aggregates all the benchmarks and gives an overall breakdown. This is generally not a good idea if the individual tests indeed have different performance bottlenecks. You need to have a separate Topdown analysis for each of the tests. One way the `topdown-tool` can help is to to use `-i` option which will output data per configurable interval of time. You can then compare the intervals and decide on next steps.

[^1]: AI Benchmark Alpha - [https://ai-benchmark.com/alpha.html](https://ai-benchmark.com/alpha.html)
[^2]: ARM `topdown-tool` - [https://learn.arm.com/install-guides/topdown-tool/](https://learn.arm.com/install-guides/topdown-tool/)