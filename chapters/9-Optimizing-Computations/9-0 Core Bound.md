---
typora-root-url: ..\..\img
---

# Optimizing Computations {#sec:CoreBound}

In the previous chapter, we discussed how to clear the path for efficient memory accesses. Once that is done, it's time to look at how well a CPU works with the data it brings from memory. Modern applications demand a large amount of CPU computations, especially those that involve complex graphics, artificial intelligence, cryptocurrency mining, and big data processing. In this chapter, we will focus on optimizing computations which can reduce the amount of work that a CPU needs to do and improve the overall performance of a program.

When the TMA methodology is applied, inefficient computations are usually reflected in the `Core Bound` and to some extent in `Retiring` categories. The `Core Bound` category represents all the stalls inside a CPU Out-Of-Order execution engine that were not caused by memory issues. There are two main categories:

* Data dependencies between software's instructions are limiting the performance. For example, a long sequence of dependent operations may lead to low Instruction Level Parallelism (ILP) and wasting many executions slots. The next section discusses data dependency chains in more detail.
* Shortage in hardware compute resources (aka not enough execution throughput). It indicates that certain execution units are overloaded (aka execution port contention). This can happen when a workload frequently performs many instructions of the same type. For example, AI algorithms typically perform a lot of multiplications, scientific applications may run many divisions and square root operations. But there is limited number of multipliers and dividers in any given CPU core. Thus when port contention occurs, instructions queue up waiting for their turn to be executed. This type of performance bottleneck is very specific to a particular CPU microarchitecture and usually doesn't have a cure.

[TODO:] Give guidance on how to detect port contention.

In [@sec:TMA], we said that high `Retiring` metric is a good indicator of a well-performing code. The rationale behind it is that execution is not stalled and a CPU is retiring instructions at a high rate. However, sometimes it may hide the real performance problem, that is inefficient computations. A workload may be executing a lot of instructions that are too simple and not doing much useful work. In this case, the high `Retiring` metric won't translate into the high performance.

In this chapter, we will take a look at the well-known techniques like function inlining, vectorization, and loop optimizations. Those code transformations aim at reducing the total amount of executed instructions, or replacing them with a more efficient ones.
