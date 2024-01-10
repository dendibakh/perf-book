---
typora-root-url: ..\..\img
---

## Chapter Summary {.unlisted .unnumbered}

* Instruction Set Architecture (ISA) is a fundamental contract between SW and HW. ISA is an abstract model of a computer that defines the set of available operations and data types, set of registers, memory addressing, and other things. You can implement a specific ISA in many different ways. For example, you can design a "small" core that prioritizes power efficiency or a "big" core that targets high performance. 
* The details of the implementation are incapsulated in a term CPU "microarchitecture". It has been a topic that was researched by thousands of computer scientists for a long time. Through the years, many smart ideas were invented and implemented in mass-market CPUs. The most notable are pipelining, out-of-order execution, superscalar engines, speculative execution and SIMD processors. All these techniques help exploit Instruction-Level Parallelism (ILP) and improve singe-threaded performance.
* In parallel with single-threaded performance, HW designers began pushing multi-threaded performance. Vast majority or modern client-facing devices have a processor with multiple cores inside. Some cores double the number of observable CPU cores with the help of Simultaneous Multithreading (SMT). SMT allows multiple software threads to run simultaneously on the same physical core using shared resources. More recent technique in this direction is called "hybrid" processors that combines different types of cores in a single package to better support diversity of workloads.
* Memory hierarchy in modern computers includes several level of caches that reflect different tradeoffs in speed of access vs. size. L1 cache tends to be closest to a core, fast but small. L3/LLC cache is slower but also bigger. DDR is the predominant DRAM technology integrated in most platforms. DRAM modules vary in the number of ranks and memory width which may have a slight impact on system performance. Processors may have multiple memory channels to access more than one DRAM module simultaneously.
* Virtual memory is the mechanism for sharing the physical memory with all the processes running on the CPU. Programs use virtual addresses in their accesses, which get translated into physical addresses. The memory space is split into pages. The default page size on x86 is 4KB, on ARM is 16KB. Only the page address gets translated, the offset within the page is used as it is. The OS keeps the translation in the page table, which is implemented as a radix tree. There are HW features that improve the performance of address translation: mainly Translation Lookaside Buffer (TLB) and HW page walkers. Also, developers can utilize Huge Pages to mitigate the cost of address translation in some cases.
* We looked at the design of a recent Intel's GoldenCove microarchitecture. Logically, the core is split into Front-End and Back-End. Front-End consists of Branch Predictor Unit (BPU), L1-I cache, instruction fetch and decode logic, and IDQ, which feeds instructions to the CPU Back-End. The Back-End consists of OOO engine, execution units, load-store unit, L1-D cache, and a TLB hierarchy.
* Modern processors have some performance monitoring features which are encapsulated into Performance Monitoring Unit (PMU). The central place in this unit is a concept of Performance Monitoring Counters (PMC) that allow to observe specific events that happen while the program is running, for example, cache misses and branch mispredictions.

\sectionbreak



