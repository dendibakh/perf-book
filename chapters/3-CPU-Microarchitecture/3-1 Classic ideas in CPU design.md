---
typora-root-url: ..\..\img
---

## Instruction Set Architecture

The instruction set is the vocabulary used by software to communicate with the hardware. The instruction set architecture (ISA) defines the contract between the software and the hardware. Intel x86, ARM v8, RISC-V are examples of current-day ISA that are most widely deployed. All of these are 64-bit architectures, i.e., all address computation uses 64-bit. ISA developers and CPU architects typically ensure that software or firmware that conforms to the specification will execute on any processor built using the specification. Widely deployed ISA franchises also typically ensure backward compatibility such that code written for the GenX version of a processor will continue to execute on GenX+i.

Most modern architectures can be classified as general purpose register-based, load-store architectures where the operands are explicitly specified, and memory is accessed only using load and store instructions. In addition to providing the basic functions in the ISA such as load, store, control, scalar arithmetic operations using integers and floating-point, the widely deployed architectures continue to enhance their ISA to support new computing paradigms. These include enhanced vector processing instructions (e.g., Intel AVX2, AVX512, ARM SVE) and matrix/tensor instructions (Intel AMX). Software mapped to use these advanced instructions typically provide orders of magnitude improvement in performance. 

Modern CPUs support 32b and 64b precision for arithmetic operations. With the fast-evolving field of deep learning, the industry has a renewed interest in alternate numeric formats for variables to drive significant performance improvements. Research has shown that deep learning models perform just as good, using fewer bits to represent the variables, saving on both compute and memory bandwidth. As a result, several CPU franchises have recently added support for lower precision data types such as 8bit integers (int8, e.g., Intel VNNI), 16b floating-point (fp16, bf16) in the ISA, in addition to the traditional 32-bit and 64-bit formats for arithmetic operations.

## Pipelining

Pipelining is the foundational technique used to make CPUs fast wherein multiple instructions are overlapped during their execution. Pipelining in CPUs drew inspiration from the automotive assembly lines. The processing of instructions is divided into stages. The stages operate in parallel, working on different parts of different instructions. DLX is an example of a simple 5-stage pipeline defined by [@Hennessy] and consists of:

1. Instruction fetch (IF)
2. Instruction decode (ID)
3. Execute (EXE)
4. Memory access (MEM)
5. Write back (WB)

![Simple 5-stage pipeline diagram.](../../img/uarch/Pipelining.png){#fig:Pipelining width=70%}

Figure @fig:Pipelining shows an ideal pipeline view of the 5-stage pipeline CPU. In cycle 1, instruction x enters the IF stage of the pipeline. In the next cycle, as instruction x moves to the ID stage, the next instruction in the program enters the IF stage, and so on. Once the pipeline is full, as in cycle 5 above, all pipeline stages of the CPU are busy working on different instructions. Without pipelining, instruction `x+1` couldn't start its execution until instruction `x` finishes its work.

Most modern CPUs are deeply pipelined, aka super pipelined. The throughput of a pipelined CPU is defined as the number of instructions that complete and exit the pipeline per unit of time. The latency for any given instruction is the total time through all the stages of the pipeline. Since all the stages of the pipeline are linked together, each stage must be ready to move to the next instruction in lockstep. The time required to move an instruction from one stage to the other defines the basic machine cycle or clock for the CPU. The value chosen for the clock for a given pipeline is defined by the slowest stage of the pipeline. CPU hardware designers strive to balance the amount of work that can be done in a stage as this directly defines the frequency of operation of the CPU. Increasing the frequency improves performance and typically involves balancing and re-pipelining to eliminate bottlenecks caused by the slowest pipeline stages. 

In an ideal pipeline that is perfectly balanced and doesn’t incur any stalls, the time per instruction in the pipelined machine is given by 
$$
\textrm{Time per instruction on pipelined machine} = \frac{\textrm{Time per instruction on nonpipelined machine}}{\textrm{Number of pipe stages}}
$$
In real implementations, pipelining introduces several constraints that limit the ideal model shown above. Pipeline hazards prevent the ideal pipeline behavior resulting in stalls. The three classes of hazards are structural hazards, data hazards, and control hazards. Luckily for the programmer, in modern CPUs, all classes of hazards are handled by the hardware.

* **Structural hazards** are caused by resource conflicts. To a large extent, they could be eliminated by replicating the hardware resources, such as using multi-ported registers or memories. However, eliminating all such hazards could potentially become quite expensive in terms of silicon area and power.

* **Data hazards** are caused by data dependencies in the program and are classified into three types:

  *Read-after-write* (RAW) hazard requires dependent read to execute after write. It occurs when an instruction x+1 reads a source before a previous instruction x writes to the source, resulting in the wrong value being read. CPUs implement data forwarding from a later stage of the pipeline to an earlier stage (called "*bypassing*") to mitigate the penalty associated with the RAW hazard. The idea is that results from instruction x can be forwarded to instruction x+1 before instruction x is fully completed. If we take a look at the example:

  ```
  R1 = R0 ADD 1
  R2 = R1 ADD 2
  ```

  There is a RAW dependency for register R1. If we take the value directly after addition `R0 ADD 1` is done (from the `EXE` pipeline stage), we don't need to wait until the `WB` stage finishes, and the value will be written to the register file. Bypassing helps to save a few cycles. The longer the pipeline, the more effective bypassing becomes.

  *Write-after-read* (WAR) hazard requires dependent write to execute after read. It occurs when an instruction x+1 writes a source before a previous instruction x reads the source, resulting in the wrong new value being read. WAR hazard is not a true dependency and is eliminated by a technique called [register renaming](https://en.wikipedia.org/wiki/Register_renaming)[^1]. It is a technique that abstracts logical registers from physical registers. CPUs support register renaming by keeping a large number of physical registers. Logical (architectural) registers, the ones that are defined by the ISA, are just aliases over a wider register file. With such decoupling of [architectural state](https://en.wikipedia.org/wiki/Architectural_state)[^3], solving WAR hazards is simple; we just need to use a different physical register for the write operation. For example:

  ```
  R1 = R0 ADD 1
  R0 = R2 ADD 2
  ```

  There is a WAR dependency for register R0. Since we have a large pool of physical registers, we can simply rename all the occurrences of `R0` register starting from the write operation and below. Once we eliminated WAR hazard by renaming register `R0`, we can safely execute the two operations in any order.

  *Write-after-write* (WAW) hazard requires dependent write to execute after write. It occurs when instruction x+1 writes a source before instruction x writes to the source, resulting in the wrong order of writes. WAW hazards are also eliminated by register renaming, allowing both writes to execute in any order while preserving the correct final result.

* **Control hazards** are caused due to changes in the program flow. They arise from pipelining branches and other instructions that change the program flow. The branch condition that determines the direction of the branch (taken vs. not-taken) is resolved in the execute pipeline stage. As a result, the fetch of the next instruction cannot be pipelined unless the control hazard is eliminated. Techniques such as dynamic branch prediction and speculative execution described in the next section are used to overcome control hazards.

## Exploiting Instruction Level Parallelism (ILP)

Most instructions in a program lend themselves to be pipelined and executed in parallel, as they are independent. Modern CPUs implement a large menu of additional hardware features to exploit such instruction-level parallelism (ILP). Working in concert with advanced compiler techniques, these hardware features provide significant performance improvements. 

### OOO Execution

The pipeline example in Figure @fig:Pipelining shows all instructions moving through the different stages of the pipeline in-order, i.e., in the same order as they appear in the program. Most modern CPUs support out-of-order (OOO) execution, i.e., sequential instructions can enter the execution pipeline stage in any arbitrary order only limited by their dependencies. OOO execution CPUs must still give the same result as if all instructions were executed in the program order. An instruction is called *retired* when it is finally executed, and its results are correct and visible in the [architectural state](https://en.wikipedia.org/wiki/Architectural_state). To ensure correctness, CPUs must retire all instructions in the program order. OOO is primarily used to avoid underutilization of CPU resources due to stalls caused by dependencies, especially in superscalar engines described in the next section. 

Dynamic scheduling of these instructions is enabled by sophisticated hardware structures such as scoreboards and techniques such as register renaming to reduce data hazards. [Tomasulo algorithm](https://en.wikipedia.org/wiki/Tomasulo_algorithm)[^4] implemented in the IBM360 and [Scoreboading](https://en.wikipedia.org/wiki/Scoreboarding)[^5] implemented in the CDC6600 in the 1960s are pioneering efforts to support dynamic scheduling and out-of-order execution that have influenced all modern CPU architectures. The scoreboard hardware is used to schedule the in-order retirement and all machine state updates. It keeps track of data dependencies of every instruction and where in the pipe the data is available. Most implementations strive to balance the hardware cost with the potential return. Typically, the size of the scoreboard determines how far ahead the hardware can look for scheduling such independent instructions. 

![The concept of Out-Of-Order execution.](../../img/uarch/OOO.png){#fig:OOO width=80%}

Figure @fig:OOO details the concept underlying out-of-order execution with an example. Assume instruction x+1 cannot execute in cycles 4 and 5 due to some conflict. An in-order CPU would stall all subsequent instructions from entering the EXE pipeline stage. In an OOO CPU, subsequent instructions that do not have any conflicts (e.g., instruction x+2) can enter and complete its execution. All instructions still retire in order, i.e., the instructions complete the WB stage in the program order.

### Superscalar Engines and VLIW

Most modern CPUs are superscalar i.e., they can issue more than one instruction in a given cycle. Issue-width is the maximum number of instructions that can be issued during the same cycle. Typical issue-width of current generation CPUs ranges from 2-6. To ensure the right balance, such superscalar engines also support more than one execution unit and/or pipelined execution units. CPUs also combine superscalar capability with deep pipelines and out-of-order execution to extract the maximum ILP for a given piece of software. 

![The pipeline diagram for a simple 2-way superscalar CPU.](../../img/uarch/SuperScalar.png){#fig:SuperScalar width=55%}

Figure @fig:SuperScalar shows an example CPU that supports 2-wide issue width, i.e., in each cycle, two instructions are processed in each stage of the pipeline. Superscalar CPUs typically support multiple, independent execution units to keep the instructions in the pipeline flowing through without conflicts. Replicated execution units increase the throughput of the machine in contrast with simple pipelined processors shown in figure @fig:Pipelining.

Architectures such as the Intel Itanium moved the burden of scheduling a superscalar, multi-execution unit machine from the hardware to the compiler using a technique known as VLIW - Very Long Instruction Word. The rationale is to simplify the hardware by requiring the compiler to choose the right mix of instructions to keep the machine fully utilized. Compilers can use techniques such as software pipelining, loop unrolling, etc. to look further ahead than can be reasonably supported by hardware structures to find the right ILP. 

### Speculative Execution {#sec:SpeculativeExec}

As noted in the previous section, control hazards can cause significant performance loss in a pipeline if instructions are stalled until the branch condition is resolved. One technique to avoid this performance loss is hardware branch prediction logic to predict the likely direction of branches and allow executing instructions from the predicted path (speculative execution).

Let's consider a short code example in @lst:Speculative. For a processor to understand which function it should execute next, it should know whether the condition `a < b` is false or true. Without knowing that, the CPU waits until the result of the branch instruction will be determined, as shown in figure @fig:NoSpeculation. 

Listing: Speculative execution

~~~~ {#lst:Speculative .cpp}
if (a < b)
  foo();
else
  bar();
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

<div id="fig:Speculative">
![No speculation](../../img/uarch/Speculative1.png){#fig:NoSpeculation width=60%}


![Speculative execution](../../img/uarch/Speculative2.png){#fig:SpeculativeExec width=60%}

The concept of speculative execution.
</div>

With speculative execution, the CPU takes a guess on an outcome of the branch and initiates processing instructions from the chosen path. Suppose a processor predicted that condition `a < b` will be evaluated as true. It proceeded without waiting for the branch outcome and speculatively called function `foo` (see figure @fig:SpeculativeExec, speculative work is marked with `*`). State changes to the machine cannot be committed until the condition is resolved to ensure that the architecture state of the machine is never impacted by speculatively executing instructions. In the example above, the branch instruction compares two scalar values, which is fast. But in reality, a branch instruction can be dependent on a value loaded from memory, which can take hundreds of cycles. If the prediction turns out to be correct, it saves a lot of cycles. However, sometimes the prediction is incorrect, and the function `bar` should be called instead. In such a case, the results from the speculative execution must be squashed and thrown away. This is called the branch misprediction penalty, which we discuss in [@sec:BbMisp].

To track the progress of speculation, the CPU supports a structure called the reorder buffer (ROB). The ROB maintains the status of all instruction execution and retires instructions in-order. Results from speculative execution are written to the ROB and are committed to the architecture registers, in the same order as the program flow and only if the speculation is correct. CPUs can also combine speculative execution with out-of-order execution and use the ROB to track both speculation and out-of-order execution. 

## Exploiting Thread Level Parallelism

Techniques described previously rely on the available parallelism in a program to speed up execution. In addition, CPUs support techniques to exploit parallelism across processes and/or threads executing on the CPU. A hardware multi-threaded CPU supports dedicated hardware resources to track the state (aka context) of each thread independently in the CPU instead of tracking the state for only a single executing thread or process. The main motivation for such a multi-threaded CPU is to switch from one context to another with the smallest latency (without incurring the cost of saving and restoring thread context) when a thread is blocked due to a long latency activity such as memory references.  

### Simultaneous Multithreading

Modern CPUs combine ILP techniques and multi-threading by supporting simultaneous multi-threading to eke out the most efficiency from the available hardware resources. Instructions from multiple threads execute concurrently in the same cycle. Dispatching instructions simultaneously from multiple threads increases the probability of utilizing the available superscalar resources, improving the overall performance of the CPU. In order to support SMT, the CPU must replicate hardware to store the thread state (program counter, registers). Resources to track OOO and speculative execution can either be replicated or partitioned across threads. Typically cache resources are dynamically shared amongst the hardware threads. Modern multi-threaded CPUs  support either two threads (SMT2) or four threads (SMT4).

## Memory Hierarchy {#sec:MemHierar}

In order to effectively utilize all the hardware resources provisioned in the CPU, the machine needs to be fed with the right data at the right time. Understanding the memory hierarchy is critically important to deliver on the performance capabilities of a CPU. Most programs exhibit the property of locality; they don’t access all code or data uniformly. A CPU memory hierarchy is built on two fundamental properties:

* **Temporal locality**: when a given memory location was accessed, it is likely that the same location is accessed again in the near future. Ideally, we want this information to be in the cache next time we need it.
* **Spatial locality:** when a given memory location was accessed, it is likely that nearby locations are accessed in the near future. This refers to placing related data close to each other. When the program reads a single byte from memory, typically, a larger chunk of memory (cache line) is fetched because very often, the program will require that data soon.

This section provides a summary of the key attributes of memory hierarchy systems supported on modern CPUs.

### Cache Hierarchy

A cache is the first level of the memory hierarchy for any request (for code or data) issued from the CPU pipeline. Ideally, the pipeline performs best with an infinite cache with the smallest access latency. In reality, the access time for any cache increases as a function of the size. Therefore, the cache is organized as a hierarchy of small, fast storage blocks closest to the execution units, backed up by larger, slower blocks. A particular level of the cache hierarchy can be used exclusively for code (instruction cache, i-cache) or for data (data cache, d-cache), or shared between code and data (unified cache). Furthermore, some levels of the hierarchy can be private to a particular CPU, while other levels can be shared among CPUs. 

Caches are organized as blocks with a defined block size (**cache line**). The typical cache line size in modern CPUs is 64 bytes. Caches closest to the execution pipeline typically range in size from 8KiB to 32KiB. Caches further out in the hierarchy can be 64KiB to 16MiB in modern CPUs. The architecture for any level of a cache is defined by the following four attributes.

#### Placement of data within the cache. 

The address for a request is used to access the cache. In direct-mapped caches, a given block address can appear only in one location in the cache and is defined by a mapping function shown below. 
$$
\textrm{Number of Blocks in the Cache} = \frac{\textrm{Cache Size}}{\textrm{Cache Block Size}}
$$
$$
\textrm{Direct mapped location} = \textrm{(block address)  mod  (Number of Blocks in the Cache )}
$$

In a fully associative cache, a given block can be placed in any location in the cache. 

An intermediate option between the direct mapping and fully associative mapping is a set-associative mapping. In such a cache, the blocks are organized as sets, typically each set containing 2,4 or 8 blocks. A given address is first mapped to a set. Within a set, the address can be placed anywhere, among the blocks in that set. A cache with m blocks per set is described as an m-way set-associative cache. The formulas for a set-associative cache are:
$$
\textrm{Number of Sets in the Cache} = \frac{\textrm{Number of Blocks in the Cache}}{\textrm{Number of Blocks per Set (associativity)}}
$$
$$
\textrm{Set (m-way) associative location} = \textrm{(block address)  mod  (Number of Sets in the Cache)}
$$

#### Finding data in the cache.

Every block in the m-way set-associative cache has an address tag associated with it. In addition, the tag also contains state bits such as valid bits to indicate whether the data is valid. Tags can also contain additional bits to indicate access information, sharing information, etc. that will be described in later sections. 

![Address organization for cache lookup.](../../img/uarch/CacheLookup.png){#fig:CacheLookup width=80%}

The figure @fig:CacheLookup shows how the address generated from the pipeline is used to check the caches. The lowest order address bits define the offset within a given block; the block offset bits (5 bits for 32-byte cache lines, 6 bits for 64-byte cache lines). The set is selected using the index bits based on the formulas described above. Once the set is selected, the tag bits are used to compare against all the tags in that set. If one of the tags matches the tag of the incoming request and the valid bit is set, a cache hit results. The data associated with that block entry (read out of the data array of the cache in parallel to the tag lookup) is provided to the execution pipeline. A cache miss occurs in cases where the tag is not a match.

#### Managing misses. 

When a cache miss occurs, the controller must select a block in the cache to be replaced to allocate the address that incurred the miss. For a direct-mapped cache, since the new address can be allocated only in a single location, the previous entry mapping to that location is deallocated, and the new entry is installed in its place. In a set-associative cache, since the new cache block can be placed in any of the blocks of the set, a replacement algorithm is required. The typical replacement algorithm used is the LRU (least recently used) policy, where the block that was least recently accessed is evicted to make room for the miss address. Another alternative is to randomly select one of the blocks as the victim block. Most CPUs define these capabilities in hardware, making it easier for executing software. 

#### Managing writes. 

Read accesses to caches are the most common case as programs typically read instructions, and data reads are larger than data writes. Handling writes in caches is harder, and CPU implementations use various techniques to handle this complexity. Software developers should pay special attention to the various write caching flows supported by the hardware to ensure the best performance of their code.

CPU designs use two basic mechanisms to handle writes that hit in the cache:

* In a write-through cache, hit data is written to both the block in the cache and to the next lower level of the hierarchy.
* In a write-back cache, hit data is only written to the cache. Subsequently, lower levels of the hierarchy contain stale data. The state of the modified line is tracked through a dirty bit in the tag. When a modified cache line is eventually evicted from the cache, a write-back operation forces the data to be written back to the next lower level.  

Cache misses on write operations can be handled in two ways:

* In a *write-allocate or fetch on write miss* cache, the data for the missed location is loaded into the cache from the lower level of the hierarchy, and the write operation is subsequently handled like a write hit.
* If the cache uses a *no-write-allocate policy*, the cache miss transaction is sent directly to the lower levels of the hierarchy, and the block is not loaded into the cache. 

Out of these options, most designs typically choose to implement a write-back cache with a write-allocate policy as both of these techniques try to convert subsequent write transactions into cache-hits, without additional traffic to the lower levels of the hierarchy. Write through caches typically use the no-write-allocate policy.

#### Other cache optimization techniques. 

For a programmer, understanding the behavior of the cache hierarchy is critical to extract performance from any application. This is especially true when CPU clock frequencies increase while the memory technology speeds lag behind. From the perspective of the pipeline, the latency to access any request is given by the following formula that can be applied recursively to all the levels of the cache hierarchy up to the main memory: 
$$
\textrm{Average Access Latency} = \textrm{Hit Time } + \textrm{ Miss Rate } \times \textrm{ Miss Penalty}
$$
Hardware designers take on the challenge of reducing the hit time and miss penalty through many novel micro-architecture techniques. Fundamentally, cache misses stall the pipeline and hurt performance. The miss rate for any cache is highly dependent on the cache architecture (block size, associativity) and the software running on the machine. As a result, optimizing the miss rate becomes a hardware-software co-design effort. As described in the previous sections, CPUs provide optimal hardware organization for the caches. Additional techniques that can be implemented both in hardware and software to minimize cache miss rates are described below.

##### HW and SW Prefetching. {#sec:HwPrefetch}

One method to reduce a cache miss and the subsequent stall is to prefetch instructions as well as data into different levels of the cache hierarchy prior to when the pipeline demands. The assumption is the time to handle the miss penalty can be mostly hidden if the prefetch request is issued sufficiently ahead in the pipeline. Most CPUs support implicit hardware-based prefetching that is complemented by explicit software prefetching that programmers can control. 

Hardware prefetchers observe the behavior of a running application and initiate prefetching on repetitive patterns of cache misses. Hardware prefetching can automatically adapt to the dynamic behavior of the application, such as varying data sets, and does not require support from an optimizing compiler or profiling support. Also, the hardware prefetching works without the overhead of additional address-generation and prefetch instructions. However, hardware prefetching is limited to learning and prefetching for a limited set of cache-miss patterns that are implemented in hardware.

Software memory prefetching complements the one done by the HW. Developers can specify which memory locations are needed ahead of time via dedicated HW instruction (see [@sec:memPrefetch]). Compilers can also automatically add prefetch instructions into the code to request data before it is required. Prefetch techniques need to balance between demand and prefetch requests to guard against prefetch traffic slowing down demand traffic. 

### Main Memory

Main memory is the next level of the hierarchy, downstream from the caches. Main memory uses DRAM (dynamic RAM) technology that supports large capacities at reasonable cost points. The main memory is described by three main attributes - latency, bandwidth, and capacity. Latency is typically specified by two components. Memory access time is the time elapsed between the request to when the data word is available. Memory cycle time defines the minimum time required between two consecutive accesses to the memory. 

DDR (double data rate) DRAM technology is the predominant DRAM technology supported by most CPUs. Historically, DRAM bandwidths have improved every generation while the DRAM latencies have stayed the same or even increased. The table @tbl:mem_rate shows the top data rate and the corresponding latency for the last three generations of DDR technologies. The data rate is measured as a million transfers per sec (MT/s). The latencies shown in this table correspond to the latency in the DRAM device itself. Typically, the latencies as seen from the CPU pipeline (cache miss on a load to use) are higher (in the 70ns-150ns range) due to additional latencies and queuing delays incurred in the cache controllers, memory controllers, and on-die interconnects. 

----------------------------------------
   DDR      Highest Data   Typical Read 
Generation   Rate (MT/s)   Latency (ns)
----------  ------------   -------------
  DDR3          2133          10.3

  DDR4          3200          12.5

  DDR5          6400          14

----------------------------------------

Table: The top data rate and the corresponding latency for the last three generations of DDR technologies. {#tbl:mem_rate}

New DRAM technologies such as GDDR (Graphics DDR) and HBM (High Bandwidth Memory) are used by custom processors that require higher bandwidth, not supported by DDR interfaces.

Modern CPUs support multiple, independent channels of DDR DRAM memory. Typically, each channel of memory is either 32-bit or 64-bit wide.

## Virtual Memory

Virtual memory is the mechanism to share the physical memory attached to a CPU with all the processes executing on the CPU. Virtual memory provides a protection mechanism, restricting access to the memory allocated to a given process from other processes. Virtual memory also provides relocation, the ability to load a program anywhere in physical memory without changing the addressing in the program. 

In a CPU that supports virtual memory, programs use virtual addresses for their accesses. These virtual addresses are translated to a physical address by dedicated hardware tables that provide a mapping between virtual addresses and physical addresses. These tables are referred to as page tables. The address translation mechanism is shown below. The virtual address is split into two parts. The virtual page number is used to index into the page table (the page table can either be a single level or nested) to produce a mapping between the virtual page number and the corresponding physical page. The page offset from the virtual address is then used to access the physical memory location at the same offset in the mapped physical page. A page fault results if a requested page is not in the main memory. The operating system is responsible for providing hints to the hardware to handle page faults such that one of the least recently used pages can be swapped out to make space for the new page.

![Address organization for cache lookup.](../../img/uarch/VirtualMem.png){#fig:VirtualMem width=70%}

CPUs typically use a hierarchical page table format to map virtual address bits efficiently to the available physical memory. A page miss in such a system would be expensive, requiring traversing through the hierarchy. To reduce the address translation time, CPUs support a hardware structure called translation lookaside buffer (TLB) to cache the most recently used translations.

## SIMD Multiprocessors {#sec:SIMD}

Another variant of multiprocessing that is widely used for certain workloads is referred to as SIMD (Single Instruction, Multiple Data) multiprocessors, in contrast to the MIMD approach described in the previous section. As the name indicates, in SIMD processors, a single instruction typically operates on many data elements in a single cycle using many independent functional units. Scientific computations on vectors and matrices lend themselves well to SIMD architectures as every element of a vector or matrix needs to be processed using the same instruction. SIMD multiprocessors are used primarily for such special purpose tasks that are data-parallel and require only a limited set of functions and operations.

Figure @fig:SIMD shows scalar and SIMD execution modes for the code listed in @lst:SIMD. In a traditional SISD (Single Instruction, Single Data) mode, addition operation is separately applied to each element of array `a` and `b`. However, in SIMD mode, addition is applied to multiple elements at the same time. SIMD CPUs support execution units that are capable of performing different operations on vector elements. The data elements themselves can be either integers or floating-point numbers. SIMD architecture allows more efficient processing of a large amount of data and works best for data-parallel applications that involve vector operations.

Listing: SIMD execution

~~~~ {#lst:SIMD .cpp}
double *a, *b, *c;
for (int i = 0; i < N; ++i) {
  c[i] = a[i] + b[i];
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Example of scalar and SIMD operations.](../../img/uarch/SIMD.png){#fig:SIMD width=80%}

Most of the popular CPU architectures feature vector instructions, including x86, PowerPC, ARM, and RISC-V. In 1996 Intel released a new instruction set, MMX, which was a SIMD instruction set that was designed for multimedia applications. Following MMX, Intel introduced new instruction sets with added capabilities and increased vector size: SSE, AVX, AVX2, AVX512. As soon as the new instruction sets became available, work began to make them usable to software engineers. At first, the new SIMD instructions were programmed in assembly. Later, special compiler intrinsics were introduced. Today all of the major compilers support vectorization for the popular processors.

[^1]: Register renaming - [https://en.wikipedia.org/wiki/Register_renaming](https://en.wikipedia.org/wiki/Register_renaming).

[^3]: Architectural state - [https://en.wikipedia.org/wiki/Architectural_state](https://en.wikipedia.org/wiki/Architectural_state).
[^4]: Tomasulo algorithm - [https://en.wikipedia.org/wiki/Tomasulo_algorithm](https://en.wikipedia.org/wiki/Tomasulo_algorithm).
[^5]: Scoreboarding - [https://en.wikipedia.org/wiki/Scoreboarding](https://en.wikipedia.org/wiki/Scoreboarding).

