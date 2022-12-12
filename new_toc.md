Planned Table Of Contents (second edition)

_changes are highlighted as_ `[todo]`.


Cover `[new design]`

Preface

1 Introduction

    1.1 Why Do We Still Need Performance Tuning?
    1.2 Who Needs Performance Tuning?
    1.3 What Is Performance Analysis?
    1.4 What is discussed in this book?
    1.5 What is not in this book?
    1.6 Chapter Summary

Part1. Performance analysis on a modern CPU

    2 Measuring Performance
    2.1 Noise In Modern Systems
    2.2 Measuring Performance In Production
    2.3 Automated Detection of Performance Regressions
    2.4 Manual Performance Testing
    2.5 Software and Hardware Timers
    2.6 Microbenchmarks
    2.7 Chapter Summary

3 CPU Microarchitecture

    3.1 Instruction Set Architecture
    3.2 Pipelining
    3.3 Exploiting Instruction Level Parallelism (ILP)
    3.4 Exploiting Thread Level Parallelism
    3.5 Memory Hierarchy
    3.6 Virtual Memory
    3.7 SIMD Multiprocessors
    3.8 Modern CPU design
    3.9 Performance Monitoring Unit

4 Terminology and metrics in performance analysis

    4.1 Retired vs. Executed Instruction
    4.2 CPU Utilization
    4.3 CPI & IPC
    4.4 UOPs (micro-ops)
    4.5 Pipeline Slot
    4.6 Core vs. Reference Cycles
    4.7 Cache miss
    4.8 Mispredicted branch
                                        [add more secondary metrics like MPKI, BrMissPKI, etc.]

`[New chapter: Power and performance]`

5 Performance Analysis Approaches

    5.1 Code Instrumentation            [add usages of marker APIs, e.g. perf_event_open; libpfm4; PAPI; likwid]
    5.2 Tracing                         
    5.3 Workload Characterization
    5.4 Sampling
    5.5 Roofline Performance Model
    5.6 Static Performance Analysis     [Expand on how to use UICA in performance work]
    5.7 Compiler Optimization Reports
    5.8 Chapter Summary

6 CPU Features For Performance Analysis `[expand with information about AMD and ARM PMU capabilities]`

    6.1 Top-Down Microarchitecture Analysis
    6.2 Last Branch Record
    6.3 Processor Event-Based Sampling
    6.4 Intel Processor Traces
    6.5 Chapter Summary

`[New chapter: Overview of Performance Analysis Tools]`

    Intel Vtune
    AMD uprof
    Apple Instruments
    Linux perf
    Other: KUTrace, KDAB hotspots, Netflix FlameScope, Tracy, Optick, Superluminal

Part2. Source Code Tuning For CPU

    7 CPU Front-End Optimizations
    7.1 Machine code layout
    7.2 Basic Block
    7.3 Basic block placement
    7.4 Basic block alignment
    7.5 Function splitting
    7.6 Function grouping
    7.7 Profile Guided Optimizations    [Expand on Bolt and Propeller]
    7.8 Optimizing for ITLB             [Expand on huge pages code]
    7.9 Chapter Summary

8 CPU Back-End Optimizations

    8.1 Memory Bound
        8.1.1 Cache-Friendly Data Structures
        8.1.2 Explicit Memory Prefetching
        8.1.3 Optimizing For DTLB       [Expand on huge pages and page walks]
    8.2 Core Bound
        8.2.1 Inlining Functions
        8.2.2 Loop Optimizations        [add unroll and jam]
        8.2.3 Vectorization             [add Google Highway library]
        8.2.4 Compiler Intrinsics       [expand with examples and typical use cases]
    8.3 Chapter Summary

9 Optimizing Bad Speculation

    9.1 Replace branches with lookup
    9.2 Replace branches with predication
    9.3 Chapter Summary

`[New chapter: Architecture-specific optimizations]`

    performance considerations on x86, ARM, and RISC-V (similarities and differences)
    application-specific instructions (e.g. AES, VNNI, AVX512FP16 and AVX512BF16)
    instruction latencies and throughput at uops.info,
    memory order violation, 4K aliasing, etc.

10 Other Tuning Areas `[add: Optimizing IO]`

    10.1 Compile-Time Computations
    10.2 Compiler Intrinsics [move to core bound]
    10.3 Cache Warming
    10.4 Detecting Slow FP Arithmetic
    10.5 System Tuning

11 Optimizing Multithreaded Applications `[to improve: hybrid architectures, affinity and task scheduling.]`

    11.1 Performance Scaling And Overhead
    11.2 Parallel Efficiency Metrics
    11.3 Analysis With Intel VTune Profiler
    11.4 Analysis with Linux Perf
    11.5 Analysis with Coz
    11.6 Analysis with eBPF and GAPP
    11.7 Detecting Coherence Issues
    11.8 Chapter Summary

`[New chapter: Current and Future Trends in HW and SW Performance]`

Epilog

Glossary

Acknowledgements `[moved from the beginning]`

References

Appendix A. Reducing Measurement Noise

Appendix B. The LLVM Vectorizer