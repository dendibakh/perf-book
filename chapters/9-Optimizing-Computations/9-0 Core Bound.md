# Optimizing Computations {#sec:CoreBound}

In the previous chapter, we discussed how to clear the path for efficient memory access. Once that is done, it's time to look at how well a CPU works with the data it brings from memory. Modern applications demand a large amount of CPU computations, especially applications involving complex graphics, artificial intelligence, cryptocurrency mining, and big data processing. In this chapter, we will focus on optimizing computations that can reduce the amount of work a CPU needs to do and improve the overall performance of a program.

When the TMA methodology is applied, inefficient computations are usually reflected in the `Core Bound` and, to some extent, in the `Retiring` categories. The `Core Bound` category represents all the stalls inside a CPU out-of-order execution engine that were not caused by memory issues. There are two main categories:

* Data dependencies between software instructions are limiting the performance. For example, a long sequence of dependent operations may lead to low Instruction Level Parallelism (ILP) and wasting many execution slots. The next section discusses data dependency chains in more detail.
* A shortage in hardware computing resources. This indicates that certain execution units are overloaded (also known as *execution port contention*). This can happen when a workload frequently performs many instructions of the same type. For example, AI algorithms typically perform a lot of multiplications, scientific applications may run many divisions and square root operations. However, there is a limited number of multipliers and dividers in any given CPU core. Thus when port contention occurs, instructions queue up waiting for their turn to be executed. This type of performance bottleneck is very specific to a particular CPU microarchitecture and usually doesn't have a cure.

[TODO]: Give guidance on how to detect port contention.

In [@sec:TMA], we said that a high `Retiring` metric is a good indicator of well-performing code. The rationale behind it is that execution is not stalled and a CPU is retiring instructions at a high rate. However, sometimes it may hide the real performance problem, that is, inefficient computations. A workload may be executing a lot of instructions that are too simple and not doing much useful work. In this case, the high `Retiring` metric won't translate into high performance.

In this chapter, we will take a look at well-known techniques like function inlining, vectorization, and loop optimizations. Those code transformations aim to reduce the total amount of executed instructions or replace them with more efficient ones.
