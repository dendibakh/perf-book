Planned Table Of Contents (second edition)

_changes are highlighted with square brackets as_ [todo].

Cover [new design]

Preface

**1 Introduction**

    1.1 Why Do We Still Need Performance Tuning?
    1.2 Who Needs Performance Tuning?
    1.3 What Is Performance Analysis?
    1.4 What is discussed in this book?
    1.5 What is not in this book?
    [Exercises: perf-ninja]
    1.6 Chapter Summary

**Part1. Performance analysis on a modern CPU**

**2 Measuring Performance**

    2.1 Noise In Modern Systems
    2.2 Measuring Performance In Production
    2.3 Automated Detection of Performance Regressions
    2.4 Manual Performance Testing
    2.5 Software and Hardware Timers
    2.6 Microbenchmarks
    2.7 Chapter Summary
    [add questions/exercises]
	
**3 CPU Microarchitecture**

    3.1 Instruction Set Architecture
    3.2 Pipelining
    3.3 Exploiting Instruction Level Parallelism (ILP)
    3.4 Exploiting Thread Level Parallelism
    3.5 Memory Hierarchy
    3.6 Virtual Memory
    3.7 SIMD Multiprocessors
    [hybrid CPUs]
    3.8 Modern CPU design
    3.9 Performance Monitoring Unit
    [add chapter Summary]
    [add questions/exercises]
	
**4 Terminology and metrics in performance analysis**

    4.1 Retired vs. Executed Instruction
    4.2 CPU Utilization
    4.3 CPI & IPC
    4.4 UOPs (micro-ops)
    4.5 Pipeline Slot
    4.6 Core vs. Reference Cycles
    4.7 Cache miss
    4.8 Mispredicted branch
    [add more secondary metrics like MPKI, BrMissPKI, etc.]
    [add chapter Summary]
    [add questions/exercises]

**[5. New chapter: Power and performance]**

**6 Performance Analysis Approaches**

    6.1 Code Instrumentation            [add usages of marker APIs, e.g. perf_event_open; libpfm4; PAPI; likwid]
    6.2 Tracing                         
    6.3 Workload Characterization
    6.4 Sampling
    6.5 Roofline Performance Model
    6.6 Static Performance Analysis     [Expand on how to use UICA in performance work]
    6.7 Compiler Optimization Reports
    [add questions/exercises: what would you use to measure X; go run perf record]
    6.8 Chapter Summary

**7 CPU Features For Performance Analysis** [expand with information about AMD and ARM PMU capabilities]

    7.1 Top-Down Microarchitecture Analysis
    7.2 Last Branch Record
    7.3 Processor Event-Based Sampling
    7.4 Intel Processor Traces
    [add questions/exercises]
    7.5 Chapter Summary
    
**[New chapter: 8 Overview of Performance Analysis Tools]**

    Intel Vtune - AMD uprof - Apple Instruments - Linux perf
    Other: KUTrace, KDAB hotspots, Netflix FlameScope, [Tracy, Optick, Superluminal]
    [Windows ETW]
    [Continuous Profilers]
    [add questions/exercises]

**Part2. Source Code Tuning For CPU**

	
**9 Optimizing Memory Accesses**

	9.1 Cache-Friendly Data Structures
    9.2 Explicit Memory Prefetching
    9.3 Optimizing For DTLB       [Expand on huge pages and page walks]
	[add questions/exercises]
	
**10 Optimizing Computations**

	10.1 Inlining Functions
    10.2 Loop Optimizations        [add unroll and jam]
    10.3 Vectorization             [add Google Highway library]
    10.4 Compiler Intrinsics       [expand with examples and typical use cases]
    [add questions/exercises]
    10.5 Chapter Summary
	
**11 Optimizing Bad Speculation**
	
    11.1 Replace branches with lookup
    11.2 Replace branches with predication
    11.3 Chapter Summary
	[add questions/exercises]

**12 CPU Front-End Optimizations**
	
	12.1 Machine code layout
    12.2 Basic Block
    12.3 Basic block placement
    12.4 Basic block alignment
    12.5 Function splitting
    12.6 Function grouping
    12.7 Profile Guided Optimizations    [Expand on Bolt and Propeller]
    12.8 Optimizing for ITLB             [Expand on huge pages for code]
	[add questions/exercises]
    12.9 Chapter Summary

**[New chapter: 13 Architecture-specific optimizations]**

	performance considerations on x86, ARM, and RISC-V (similarities and differences)
    application-specific instructions (e.g. AES, VNNI, AVX512FP16 and AVX512BF16)
    instruction latencies and throughput at uops.info,
    memory order violation, 4K aliasing, etc.
	[add questions/exercises]
	
**14 Other Tuning Areas**

	14.1 [Optimizing IO]
    [remove?] 14.1 Compile-Time Computations
    14.2 [Faster standard library function implementations]
    14.3 [Low Latency Techniques]
    14.4 Detecting Slow FP Arithmetic
    14.5 System Tuning
	[add questions/exercises]
	
**15 Optimizing Multithreaded Applications [to improve: hybrid architectures, affinity and task scheduling.]**

	15.1 Performance Scaling And Overhead
    15.2 Parallel Efficiency Metrics
    15.3 Analysis With Intel VTune Profiler
    15.4 Analysis with Linux Perf
    15.5 Analysis with Coz
    15.6 Analysis with eBPF and GAPP
    15.7 Detecting Coherence Issues
    15.8 Chapter Summary
	[add questions/exercises]
	
**[New chapter: 16 Current and Future Trends in HW and SW Performance]**

Epilog

Glossary

Acknowledgements [moved from the beginning]

References

Appendix A. Reducing Measurement Noise

Appendix B. The LLVM Vectorizer
