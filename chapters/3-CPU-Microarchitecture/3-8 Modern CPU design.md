

## Modern CPU Design

To see how all the concepts we talked about in this chapter are used in practice, let's take a look at the implementation of Intel’s 12th-generation core, Goldencove, which became available in 2021. This core is used as the P-core inside the Alderlake and Sapphire Rapids platforms. Figure @fig:Goldencove_diag shows the block diagram of the Goldencove core. Notice that this section only describes a single core, not the entire processor. So, we will skip the discussion about frequencies, core counts, L3 caches, core interconnects, memory latency and bandwidth, and other things.

![Block diagram of a CPU Core in the Intel GoldenCove Microarchitecture.](../../img/uarch/goldencove_block_diagram.png){#fig:Goldencove_diag width=100%}

The core is split into an in-order front-end that fetches and decodes x86 instructions into $\mu$ops and a 6-wide superscalar, out-of-order backend. The Goldencove core supports 2-way SMT. It has a 32KB first-level instruction cache (L1 I-cache), and a 48KB first-level data cache (L1 D-cache). The L1 caches are backed up by a unified 1.25MB (2MB in server chips) L2 cache. The L1 and L2 caches are private to each core. At the end of this section, we also take a look at the TLB hierarchy.

### CPU Front-End {#sec:uarchFE}

The CPU Front-End consists of several functional units that fetch and decode instructions from memory. Its main purpose is to feed prepared instructions to the CPU Back-End, which is responsible for the actual execution of instructions.

Technically, instruction fetch is the first stage to execute an instruction. But once a program reaches a steady state, the branch predictor unit (BPU) steers the work of the CPU Front-End. That is indiciated with the arrow that goes from the BPU to the instruction cache. The BPU predicts the target of all branch instructions and steers the next instruction fetch based on this prediction.

The heart of the BPU is a branch target buffer (BTB) with 12K entries containing information about branches and their targets. This information is used by the prediction algorithms. Every cycle, the BPU generates the next fetch address and passes it to the CPU Front-End.

The CPU Front-End fetches 32 bytes per cycle of x86 instructions from the L1 I-cache. This is shared among the two threads, so each thread gets 32 bytes every other cycle. These are complex, variable-length x86 instructions. First, the pre-decode stage determines and marks the boundaries of the variable instructions by inspecting the chunk. In x86, the instruction length can range from 1 to 15 bytes. This stage also identifies branch instructions. The pre-decode stage moves up to 6 instructions (also referred to as *macroinstructions*) to the Instruction Queue that is split between the two threads. The instruction queue also supports a macro-op fusion unit that detects when two macroinstructions can be fused into a single micro-operation ($\mu$op). This optimization saves bandwidth in the rest of the pipeline.

Later, up to six pre-decoded instructions are sent from the Instruction Queue to the decoder unit every cycle. The two SMT threads alternate every cycle to access this interface. The 6-way decoder converts the complex macro-Ops into fixed-length $\mu$ops. Decoded $\mu$ops are queued into the Instruction Decode Queue (IDQ), labeled as "$\mu$op Queue" on the diagram.

A major performance-boosting feature of the Front-End is the $\mu$op Cache. Also, you could often see people call it Decoded Stream Buffer (DSB). The motivation is to cache the macro-ops to $\mu$ops conversion in a separate structure that works in parallel with the L1 I-cache. When the BPU generates a new address to fetch, the $\mu$op Cache is also checked to see if the $\mu$ops translations are already available. Frequently occurring macro-ops will hit in the $\mu$op Cache, and the pipeline will avoid repeating the expensive pre-decode and decode operations for the 32-byte bundle. The $\mu$op Cache can provide eight $\mu$ops per cycle and can hold up to 4K entries.

Some very complicated instructions may require more $\mu$ops than decoders can handle. $\mu$ops for such instruction are served from the Microcode Sequencer (MSROM). Examples of such instructions include hardware operation support for string manipulation, encryption, synchronization, and others. Also, MSROM keeps the microcode operations to handle exceptional situations like branch misprediction (which requires a pipeline flush), floating-point assist (e.g., when an instruction operates with a denormalized floating-point value), and others. MSROM can push up to 4 $\mu$ops per cycle into the IDQ.

The Instruction Decode Queue (IDQ) provides the interface between the in-order frontend and the out-of-order backend. The IDQ queues up the $\mu$ops in order and can hold 144 $\mu$ops per logical processor in single thread mode, or 72 $\mu$ops per thread when SMT is active. This is where the in-order CPU Front-End finishes and the out-of-order CPU Back-End starts.

### CPU Back-End {#sec:uarchBE}

The CPU Back-End employs an OOO engine that executes instructions and stores results. We repeated a part of the diagram that depicts the GoldenCove OOO engine in Figure @fig:Goldencove_OOO.

The heart of the OOO engine is the 512-entry ReOrder Buffer (ROB). It serves a few purposes. First, it provides register renaming. There are only 16 general-purpose integer and 32 floating-point/SIMD architectural registers, however, the number of physical registers is much higher.[^1] Physical registers are located in a structure called the Physical Register File (PRF). There are separate PRFs for integer and floating-point/SIMD registers. The mappings from architecture-visible registers to the physical registers are kept in the register alias table (RAT).

![Block diagram of the CPU Back End of the Intel GoldenCove Microarchitecture.](../../img/uarch/goldencove_OOO.png){#fig:Goldencove_OOO width=100%}

Second, the ROB allocates execution resources. When an instruction enters the ROB, a new entry is allocated and resources are assigned to it, mainly an execution unit and the destination physical register. The ROB can allocate up to 6 $\mu$ops per cycle.

Third, the ROB tracks speculative execution. When an instruction has finished its execution, its status gets updated and it stays there until the previous instructions finish. It's done that way because instructions must retire in program order. Once an instruction retires, its ROB entry is deallocated and the results of the instruction become visible. The retiring stage is wider than the allocation: the ROB can retire 8 instructions per cycle.

There are certain operations that processors handle in a specific manner, often called idioms, which require no or less costly execution. Processors recognize such cases and allow them to run faster than regular instructions. Here are some of such cases:

* **Zeroing**: to assign zero to a register, compilers often use `XOR / PXOR / XORPS / XORPD` instructions, e.g., `XOR RAX, RAX`, which are preferred by compilers instead of the equivalent `MOV RAX, 0x0` instruction as the XOR encoding uses fewer encoding bytes. Such zeroing idioms are not executed as any other regular instruction and are resolved in the CPU front-end, which saves execution resources. The instruction later retires as usual.
* **Move elimination**: similar to the previous one, register-to-register `mov` operations, e.g., `MOV RAX, RBX`, are executed with zero cycle delay.
* **NOP instruction**: `NOP` is often used for padding or alignment purposes. It simply gets marked as completed without allocating it to the reservation station.
* **Other bypasses**: CPU architects also optimized certain arithmetic operations. For example, multiplying any number by one will always yield the same number. The same goes for dividing any number by one. Multiplying any number by zero always yields zero, etc. Some CPUs can recognize such cases at runtime and execute them with shorter latency than regular multiplication or divide.

The "Scheduler / Reservation Station" (RS) is the structure that tracks the availability of all resources for a given $\mu$op and dispatches the $\mu$op to an *execution port* once it is ready. An execution port is a pathway that connects the scheduler to its execution units. Each execution port may be connected to multiple execution units. When an instruction enters the RS, the scheduler starts tracking its data dependencies. Once all the source operands become available, the RS attempts to dispatch the $\mu$op to a free execution port. The RS has fewer entries[^4] than the ROB. It can dispatch up to 6 $\mu$ops per cycle.

We repeated a part of the diagram that depicts the GoldenCove execution engine and Load-Store unit in Figure @fig:Goldencove_BE_LSU. There are 12 execution ports:

* Ports 0, 1, 5, 6, and 10 provide integer (INT) operations, and some of them handle floating-point and vector (VEC/FP) operations.
* Ports 2, 3, and 11 are used for address generation (AGU) and for load operations. 
* Ports 4 and 9 are used for store operations (STD).
* Ports 7 and 8 are used for address generation.

![Block diagram of the execution engine and the Load-Store unit in the Intel GoldenCove Microarchitecture.](../../img/uarch/goldencove_BE_LSU.png){#fig:Goldencove_BE_LSU width=100%}

Instructions that require memory operations are handled by the Load-Store unit (ports 2, 3, 11, 4, 9, 7, and 8) that we will discuss in the next section. If an operation does not involve loading or storing data, then it will be dispatched to the execution engine (ports 0, 1, 5, 6, and 10).

For example, an `Integer Shift` operation can go only to either port 0 or 6, while a `Floating-Point Divide` operation can only be dispatched to port 0. In a situation when a scheduler has to dispatch two operations that require the same execution port, one of them will have to be delayed.

The VEC/FP stack does floating-point scalar and *all* packed (SIMD) operations. For instance, ports 0, 1, and 5 can handle ALU operations of the following types: packed integer, packed floating-point, and scalar floating-point. Integer and Vector/FP register stacks are located separately. Operations that move values from the INT stack to VEC/FP and vice-versa (e.g., convert, extract or insert) incur additional penalties.

### Load-Store Unit {#sec:uarchLSU}

The Load-Store Unit (LSU) is responsible for operations with memory. The Goldencove core can issue up to three loads (three 256-bit or two 512-bit) by using ports 2, 3, and 11. AGU stands for Address Generation Unit, which is required to access a memory location. It can also issue up to two stores (two 256-bit or one 512-bit) per cycle via ports 4, 9, 7, and 8. STD stands for Store Data.

Notice that the AGU is required for both load and store operations to perform dynamic address calculation. For example, in the instruction `vmovss DWORD PTR [rsi+0x4],xmm0`, the AGU will be responsible for calculating `rsi+0x4`, which will be used to store data from xmm0.

Once a load or a store leaves the scheduler, LSU is responsible for accessing the data. Load operations save the fetched value in a register. Store operations transfer value from a register to a location in memory. LSU has a Load Buffer (also known as Load Queue) and a Store Buffer (also known as Store Queue); their sizes are not disclosed.[^2] Both Load Buffer and Store Buffer receive operations at dispatch from the scheduler.

When a memory load request comes, the LSU queries the L1 cache using a virtual address and looks up the physical address translation in the TLB. Those two operations are initiated simultaneously. The size of the L1 D-cache is 48KB. If both operations result in a hit, the load delivers data to the integer or floating-point register and leaves the Load Buffer. Similarly, a store would write the data to the data cache and exit the Store Buffer.

In case of an L1 miss, the hardware initiates a query of the (private) L2 cache tags. While the L2 cache is being queried, a 64-byte wide fill buffer (FB) entry is allocated, which will keep the cache line once it arrives. The Goldencove core has 16 fill buffers. As a way to lower the latency, a speculative query is sent to the L3 cache in parallel with the L2 cache lookup.

If two loads access the same cache line, they will hit the same FB. Such two loads will be "glued" together and only one memory request will be initiated. LSU dynamically reorders operations, supporting both loads bypassing older loads and loads bypassing older non-conflicting stores. Also, LSU supports store-to-load forwarding when there is an older store containing all of the load's bytes, and the store's data has been produced and is available in the store queue.

In case the L2 miss is confirmed, the load continues to wait for the results of the L3 cache, which incurs much higher latency. From that point, the request leaves the core and enters the *uncore*, the term you may frequently see in profiling tools. The outstanding misses from the core are tracked in the Super Queue (SQ, not shown on the diagram), which can track up to 48 uncore requests. In a scenario of L3 miss, the processor begins to set up a memory access. Further details are beyond the scope of this chapter.

When a store modifies a memory location, the processor needs to load the full cache line, change it, and then write it back to memory. If the address to write is not in the cache, it goes through a very similar mechanism as with loads to bring that data in. The store cannot be complete until the data is written to the cache hierarchy.

Of course, there are a few optimizations done for store operations as well. First, if we're dealing with a store or multiple adjacent stores (also known as *streaming stores*) that modify an entire cache line, there is no need to read the data first as all of the bytes will be clobbered anyway. So, the processor will try to combine writes to fill an entire cache line. If this succeeds no memory read operation is needed at all.

Second, write combining enables multiple stores to be assembled and written further out in the cache hierarchy as a unit. So, if multiple stores modify the same cache line, only one memory write will be issued to the memory subsystem. All these optimizations are done inside the Store Buffer. A store instruction copies the data that will be written from a register into the Store Buffer. From there it may be written to the L1 cache or it may be combined with other stores to the same cache line. The Store Buffer capacity is limited, so it can hold requests for partial writing to a cache line only for some time. However, while the data sits in the Store Buffer waiting to be written, other load instructions can read the data straight from the store buffers (store-to-load forwarding).

Finally, if we happen to read data before overwriting it, the cache line typically stays in the cache. This behavior can be altered with the help of a *non-temporal* store, a special CPU instruction that will not keep the modified line in the cache. It is useful in situations when we know we will not need the data once we have changed it. Non-temporal stores help to utilize cache space more efficiently by not evicting other data that might be needed soon.

During a typical program execution, there could be dozens of memory accesses in flight. In most high-performance processors, the order of load and store operations is not necessarily required to be the same as the program order, which is known as a _weakly ordered memory model_. For optimization purposes, the processor can reorder memory read and write operations. Consider a situation when a load runs into a cache miss and has to wait until the data comes from memory. The processor allows subsequent loads to proceed ahead of the load that is waiting for the data. This allows later loads to finish before the earlier load and doesn't unnecessarily block the execution. Such load/store reordering enables the memory units to process multiple memory accesses in parallel, which translates directly into higher performance.

There are a few exceptions. Just like with dependencies through regular arithmetic instructions, there are memory dependencies through loads and stores. In other words, a load can depend on an earlier store and vice-versa. First of all, stores cannot be reordered with older loads:

```
Load R1, MEM_LOC_X
Store MEM_LOC_X, 0
```

If we allow the store to go before the load, then the `R1` register may read the wrong value from the memory location `MEM_LOC_X`.

Another interesting situation happens when a load consumes data from an earlier store:

```
Store MEM_LOC_X, 0
Load R1, MEM_LOC_X
```

If a load consumes data from a store that hasn't yet finished, we should not allow the load to proceed. But what if we don't yet know the address of the store? In this case, the processor predicts whether there will be any potential data forwarding between loads and stores and if reordering is safe. This is known as _memory disambiguation_. When a load starts executing, it has to be checked against all older stores for potential store forwarding. There are four possible scenarios:

* Prediction: Not dependent; Outcome: Not dependent. This is a case of a successful memory disambiguation, which yields optimal performance.
* Prediction: Dependent; Outcome: Not dependent. In this case, the processor was overly conservative and did not let the load go ahead of the store. This is a missed opportunity for performance optimization.
* Prediction: Not dependent; Outcome: Dependent. This is a _memory order violation_. Similar to the case of a branch misprediction, the processor has to flush the pipeline, roll back the execution and start over. It is very costly.
* Prediction: Dependent; Outcome: Dependent. There is a memory dependency between a load and a store, and the processor predicted it correctly. No missed opportunities.

It's worth mentioning that forwarding from a store to a load occurs in real code quite often. In particular, any code that uses read-modify-write accesses to its data structures is likely to trigger these sorts of problems. Due to the large out-of-order window, the CPU can easily attempt to process multiple read-modify-write sequences at once, so the read of one sequence can occur before the write of the previous sequence is complete. One such example is presented in [@sec:UarchSpecificIssues].

### TLB Hierarchy

Recall from [@sec:TLBs] that translations from virtual to physical addresses are cached in the TLB. Golden Cove's TLB hierarchy is presented in Figure @fig:GLC_TLB. Similar to a regular data cache, it has two levels, where level 1 has separate instances for instructions (ITLB) and data (DTLB). L1 ITLB has 256 entries for regular 4K pages and covers 1MB of memory, while L1 DTLB has 96 entries that cover 384 KB. 

![TLB hierarchy of Intel's GoldenCove microarchitecture.](../../img/uarch/GLC_TLB_hierarchy.png){#fig:GLC_TLB width=60%}

The second level of the hierarchy (STLB) caches translations for both instructions and data. It is a larger storage for serving requests that missed in the L1 TLBs. L2 STLB can accommodate 2048 recent data and instruction page address translations, which covers a total of 8MB of memory space. There are fewer entries available for 2MB huge pages: L1 ITLB has 32 entries, L1 DTLB has 32 entries, and L2 STLB can only use 1024 entries that are also shared with regular 4KB pages.

In case a translation was not found in the TLB hierarchy, it has to be retrieved from the DRAM by "walking" the kernel page tables. Recall that the page table is built as a radix tree of subtables, with each entry of the subtable holding a pointer to the next level of the tree. 

The key element to speed up the page walk procedure is a set of Paging-Structure Caches[^3] that cache the hot entries in the page table structure. For the 4-level page table, we have the least significant twelve bits (11:0) for page offset (not translated), and bits 47:12 for the page number. While each entry in a TLB is an individual complete translation, Paging-Structure Caches cover only the upper 3 levels (bits 47:21). The idea is to reduce the number of loads required to execute in case of a TLB miss. For example, without such caches, we would have to execute 4 loads, which would add latency to the instruction completion. But with the help of the Paging-Structure Caches, if we find a translation for levels 1 and 2 of the address (bits 47:30), we only have to do the remaining 2 loads.

The Goldencove microarchitecture has four dedicated page walkers, which allows it to process 4 page walks simultaneously. In the event of a TLB miss, these hardware units will issue the required loads into the memory subsystem and populate the TLB hierarchy with new entries. The page-table loads generated by the page walkers can hit in L1, L2, or L3 caches (details are not disclosed). Finally, page walkers can anticipate a future TLB miss and speculatively do a page walk to update TLB entries before a miss actually happens.

The Goldencove specification doesn't disclose how resources are shared between two SMT threads. But in general, caches, TLBs and execution units are fully shared to improve the dynamic utilization of those resources. On the other hand, buffers for staging instructions between major pipe stages are either replicated or partitioned. These buffers include IDQ, ROB, RAT, RS, Load Buffer and the Store Buffer. PRF is also replicated.

[^1]: There are around 300 physical general-purpose registers (GPRs) and a similar number of vector registers. The actual number of registers is not disclosed.
[^2]: Load Buffer and Store Buffer sizes are not disclosed, but people have measured 192 and 114 entries respectively.
[^3]: AMD's equivalent is called Page Walk Caches.
[^4]: People have measured  ~200 entries in the RS, however the actual number of entries is not disclosed.
