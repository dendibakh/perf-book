---
typora-root-url: ..\..\img
---

# Optimizing Computations {#sec:CoreBound}

The second type of CPU Back-End bottleneck is `Core Bound`. Technically speaking, this metric represents all the stalls inside a CPU Out-Of-Order execution engine that were not caused by memory issues. There are two main categories that represent Core Bound metric:

* Shortage in hardware compute resources. It indicates that certain execution units are overloaded (execution port contention). This can happen when a workload frequently performs lots of heavy instructions. For example, division and square root operations are served by the Divider unit and can take considerably longer latency than other instructions.
* Dependencies between software's instructions. It indicates that dependencies in the program's data- or instruction-flow are limiting the performance. For example, floating-point dependent long-latency arithmetic operations lead to low Instruction Level Parallelism (ILP).

In this subsection, we will take a look at the most well-known optimizations like function inlining, vectorization, and loop optimizations. Those optimizations aim at reducing the total amount of executed instructions, which, technically, is also helpful when the workload experience a high `Retiring` metric. But the author believes that it is appropriate to discuss them here.
