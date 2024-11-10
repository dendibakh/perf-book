### TMA On Arm Platforms

Arm CPU architects also have developed a TMA performance analysis methodology for their processors, which we will discuss next. Arm calls it "Topdown" in their documentation [@ARMNeoverseV1TopDown], so we will use their naming. At the time of this writing (late 2023), Topdown is only supported on cores designed by Arm, e.g. Neoverse N1 and Neoverse V1,[^5] and their derivatives, e.g. Ampere Altra and AWS Graviton3. Refer to the list of major CPU microarchitectures at the end of this book if you need to refresh your memory on Arm chip families. Processors designed by Apple don't support the Arm Topdown performance analysis methodology yet.

Arm Neoverse V1 is the first CPU in the Neoverse family that supports a full set of level 1 Topdown metrics: `Bad Speculation`, `Frontend Bound`, `Backend Bound`, and `Retiring`. Prior to V1 cores, Neoverse N1 supported only two L1 categories: `Frontend Stalled Cycles` and `Backend Stalled Cycles`.[^6]

To demonstrate Arm's Topdown analysis on a V1-based processor, I launched an AWS EC2 `m7g.metal` instance powered by the AWS Graviton3. Note that Topdown might not work on other non-`metal` instance types due to virtualization. I used 64-bit ARM `Ubuntu 22.04 LTS` with `Linux kernel 6.2` managed by AWS. The provided `m7g.metal` instance had 64 vCPUs and 256 GB of RAM.

I applied the Topdown methodology to [AI Benchmark Alpha](https://ai-benchmark.com/alpha.html),[^1] which is an open-source Python library for evaluating AI performance of various hardware platforms, including CPUs, GPUs, and TPUs. The benchmark relies on the TensorFlow machine learning library to measure inference and training speed for key Deep Learning models. In total, AI Benchmark Alpha consists of 42 tests, including classification, image segmentation, text translation, and others.

Arm engineers have developed the [topdown-tool](https://learn.arm.com/install-guides/topdown-tool/)[^2] that we will use below. The tool works both on Linux and Windows on ARM. On Linux, it utilizes a standard perf tool, while on Windows it uses [WindowsPerf](https://gitlab.com/Linaro/WindowsPerf/windowsperf)[^3], which is a Windows on ARM performance profiling tool. Similar to Intel's TMA, the Arm methodology employs the "drill-down" concept, i.e. you first determine the high-level performance bottleneck and then drill down for a more nuanced root cause analysis. Here is the command we used:

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

From the output above, we conclude that the benchmark doesn't suffer from branch mispredictions. Also, without a deeper understanding of the workloads involved, it's hard to say if the `Frontend Bound` of 16.5% is worth looking at, so we turn our attention to the `Backend Bound` metric, which is the main source of stalled cycles. Neoverse V1-based chips don't have the second-level breakdown, instead, the methodology suggests further exploring the problematic category by collecting a set of corresponding metrics. Here is how we drill down into the more detailed `Backend Bound` analysis:

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

In the command above, the option `-n BackendBound` collects all the metrics associated with the `Backend Bound` category as well as its descendants. The description for every metric in the output is given in [@ARMNeoverseV1TopDown]. Note, that they are quite similar to what we have discussed in [@sec:PerfMetrics], so you may want to revisit it as well. 

We don't have a goal of optimizing the benchmark, rather we want to characterize performance bottlenecks. However, if given such a task, here is how our analysis could continue. There are a substantial number of `L1 Data TLB` misses (3.8 MPKI), but then 90% of those misses hit in L2 TLB (see `L2 Unified TLB Miss Ratio`). All in all, only 0.1% of all TLB accesses result in a page table walk (see `DTLB Walk Ratio`), which suggests that it is not our primary concern, although a quick experiment that utilizes huge pages is still worthwhile.

Looking at the `L1/L2/LL Cache Effectiveness` metrics, we can spot a potential problem with data cache misses. One in ~22 accesses to the L1D cache results in a miss (see `L1D Cache Miss Ratio`), which is tolerable but still expensive. For L2, this number is one in 37 (see `L2 Cache Miss Ratio`), which is much better. However for LLC, the `LL Cache Read Miss Ratio` is unsatisfying: every 5th access results in a miss. Since this is an AI benchmark, where the bulk of the time is likely spent in matrix multiplication, code transformations like loop blocking may help (see [@sec:LoopOpts]). AI algorithms are known for being "memory hungry", however, Neoverse V1 Topdown doesn't show if there are stalls that can be attributed to saturated memory bandwidth.

The final category provides the operation mix, which can be useful in some scenarios. The percentages give us an estimate of how many instructions of a certain type were executed, including speculatively executed instructions. The numbers don't sum up to 100%, because the rest is attributed to the implicit "Others" category (not printed by the `topdown-tool`), which is about 15% in our case. We should be concerned by the low percentage of SIMD operations, especially given that the highly optimized `Tensorflow` and `numpy` libraries are used. In contrast, the percentage of integer operations and branches seems high. I checked that the majority of executed branch instructions are loop backward jumps to the next loop iteration. The high percentage of integer operations could be caused by lack of vectorization, or due to thread synchronization. [@ARMNeoverseV1TopDown] gives an example of discovering a vectorization opportunity using data from the `Speculative Operation Mix` category. 

In our case study, we ran the benchmark two times, however, in practice, one run is usually sufficient. Running the `topdown-tool` without options will collect all the available metrics using a single run. Also, the `-s combined` option will group the metrics by the L1 category, and output data in a format similar to `Intel VTune`, `toplev`, and other tools. The only practical reason for making multiple runs is when a workload has a bursty behavior with very short phases that have different performance characteristics. In such a scenario, you would like to avoid event multiplexing (see [@sec:secMultiplex]) and improve collection accuracy by running the workload multiple times. 

The AI Benchmark Alpha has various tests that could exhibit different performance characteristics. The output presented above aggregates all 42 tests and gives an overall breakdown. This is generally not a good idea if the individual tests indeed have different performance bottlenecks. You need to have a separate Topdown analysis for each of the tests. One way the `topdown-tool` can help is to use the `-i` option which will output data per configurable interval of time. You can then compare the intervals and decide on the next steps.

[^1]: AI Benchmark Alpha - [https://ai-benchmark.com/alpha.html](https://ai-benchmark.com/alpha.html)
[^2]: Arm `topdown-tool` - [https://learn.arm.com/install-guides/topdown-tool/](https://learn.arm.com/install-guides/topdown-tool/)
[^3]: WindowsPerf - [https://gitlab.com/Linaro/WindowsPerf/windowsperf](https://gitlab.com/Linaro/WindowsPerf/windowsperf)
[^5]: In September 2024, Arm published performance analysis for Neoverse V2 and V3 cores - [https://developer.arm.com/telemetry](https://developer.arm.com/telemetry)
[^6]: Performance analysis guides for Neoverse V2 and V3 cores became available after I wrote this section. See the following page - [https://developer.arm.com/telemetry](https://developer.arm.com/telemetry).
