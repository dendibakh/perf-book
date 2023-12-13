---
typora-root-url: ..\..\img
---

## Hardware-Based Sampling

Hardware-Based Sampling is another useful set of features in modern CPUs to enhance performance analysis. Since CPU vendors approach performance monitoring in different ways, those capabilities vary in not only how they are called but also what you can do with them. In Intel processors, it is called Processor Event-Based Sampling (PEBS), first introduced in NetBurst microarchitecture. A similar feature on AMD processors is called Instruction Based Sampling (IBS) and is available starting with the Family 10h generation of cores (code-named "Barcelona" and "Shanghai"). Next we will discuss those features in more details, including their similarities and differences.

### PEBS on Intel Platforms

Similar to Last Branch Record, PEBS is used while profiling the program to capture additional data with every collected sample. When a performance counter is configured for PEBS, the processor saves the set of additional data, which has a defined format and is called the PEBS record. The format of a PEBS record for Intel Skylake CPU is shown in Figure @fig:PEBS_record. The record contains the state of general-purpose registers (`EAX`, `EBX`, `ESP`, etc.), `EventingIP`, `Data Linear Address`, and `Latency value`, which will discuss later. The content layout of a PEBS record varies across different microarchitectures, see [@IntelOptimizationManual, Volume 3B, Chapter 20 Performance Monitoring].

![PEBS Record Format for 6th Generation, 7th Generation and 8th Generation Intel Core Processor Families. *© Image from [@IntelOptimizationManual, Volume 3B, Chapter 18].*](../../img/pmu-features/PEBS_record.png){#fig:PEBS_record width=90%}

Since Skylake, the PEBS record has been enhanced to collect XMM registers and LBR records. The format has been restructured where fields are grouped into Basic group, Memory group, GPR group, XMM group, and LBR group. Performance profiling tools have the option to select data groups of interest and thus reduce the record size in memory and record generation latency. By default, the PEBS record will only contain the Basic group.

One of the notable benefits of using PEBS is lower sampling overhead compared to a regular interrupt-based sampling. Recall that when the counter overflows, the CPU generates an interrupt to collect one sample. Frequently generating interrupts and having an analysis tool itself capture program state inside the interrupt service routine is very costly since it involves OS interaction. 

On the other hand, PEBS keeps a buffer to temporarily store multiple PEBS records. Suppose, we are sampling on load events using PEBS. When a performance counter is configured for PEBS, an overflow condition in the counter will not trigger an interrupt, instead it will arm the PEBS mechanism. The mechanism will then trap the next load, capture a new record and store it in the dedicated PEBS buffer area. The mechanism also takes care of clearing the counter overflow status and reloading the counter with the initial value. Only when the dedicated buffer is full, the processor raises an interrupt, and the buffer gets flushed to memory. This mechanism lowers the sampling overhead by triggering much fewer interrupts.

Linux users can check if PEBS is enabled by executing `dmesg`:

```bash
$ dmesg | grep PEBS
[    0.061116] Performance Events: PEBS fmt1+, IvyBridge events, 16-deep LBR, full-width counters, Intel PMU driver.
```

For LBR, Linux perf dumps entire contents of LBR stack with every collected sample. So, it is possible to analyze raw LBR dumps collected by Linux perf. However, for PEBS, Linux `perf` doesn't export the raw output as it does for LBR. Instead, it processes PEBS records and extracts only the subset of data depending on a particular need. So, it's not possible to access the collection of raw PEBS records with Linux `perf`. However, Linux `perf` provides some PEBS data processed from raw samples, which can be accessed by `perf report -D`. To dump raw PEBS records, one can use [`pebs-grabber`](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber)[^1] tool.

[TODO]: sort this out:

[@ComparisonPEBSIBS]

PEBS has been used to sample a variety of events to capture performance bottlenecks in multithreaded programs. In [11], PEBS and PEBS with load latency (PEBS-LL) are used to sample retired instructions and long-latency memory loads to approximate NUMA latency per instruction by dividing the total latency of the sampled loads with the number of instruction samples. A work in [36] samples memory loads and stores in each CPU core and has each core monitor effective addresses sampled by other cores using debug registers to detect false sharing. Another work in [16] samples loads that miss in L1 data caches to capture cache access patterns and identify cache conflict misses.

### IBS on AMD Platforms

[TODO]:
Instruction-Based Sampling (IBS) is a AMD64 processor feature that can be used to collect specific metrics related to instruction fetch and instruction execution.
The processor pipeline of an AMD processor consists of two separate phases: a front-end phase that fetches AMD64 instruction bytes and a back-end phase that executes “ops”.
As the phases are separate, IBS samples fetches and ops, there are two independent sampling mechanisms. Instruction fetch sampling provides information about instruction address translation look-aside buffer (ITLB) and instruction cache behavior. Instruction execution sampling provides information about instruction execution behavior by tracking the execution of a single op.

IBS selects and tags an op to be monitored. The address of the parent instruction is saved to the IBS buffer when the op is tagged. Microarchitectural events caused by the tagged op are recorded during its execution. As the address is preserved, IBS samples attribution to the instructions are precise.

### SPE on ARM Platforms

Statistical Profiling Extension (SPE)

There is a number of benefits that the PEBS mechanism brings to performance monitoring, which we will discuss in the next section.

### Precise Events

One of the major problems in profiling is pinpointing the exact instruction that caused a particular performance event. As discussed in [@sec:profiling], interrupt-based sampling is based on counting specific performance events and waiting until it overflows. When an overflow interrupt happens, it takes a processor some amount of time to stop the execution and tag the instruction that caused the overflow. This is especially difficult for modern complex out-of-order CPU architectures.

It introduces the notion of a skid, which is defined as the distance between the IP that caused the event to the IP where the event is tagged (in the IP field inside the PEBS record). Skid makes it difficult to discover the instruction causing the performance issue. Consider an application with a big number of cache misses and the hot assembly code that looks like this:

```asm
; load1 
; load2
; load3
```

The profiler might attribute `load3` as the instruction that causes a large number of cache misses, while in reality, `load1` is the instruction to blame. This usually causes a lot of confusion for beginners. Interested readers could learn more about underlying reasons for such issues on [Intel Developer Zone website](https://software.intel.com/en-us/vtune-help-hardware-event-skid)[^4].

The problem with the skid is mitigated by having the processor itself store the instruction pointer (along with other information) in a PEBS record. The `EventingIP` field in the PEBS record indicates the instruction that caused the event. This needs to be supported by the hardware and is typically available only for a subset of supported events, called "Precise Events". A complete list of precise events for specific microarchitecture can be found in  [@IntelOptimizationManual, Volume 3B, Chapter 18]. Listed below are precise events for the Skylake Microarchitecture:

```
INST_RETIRED.*
OTHER_ASSISTS.*
BR_INST_RETIRED.*
BR_MISP_RETIRED.*
FRONTEND_RETIRED.*
HLE_RETIRED.*
RTM_RETIRED.*
MEM_INST_RETIRED.*
MEM_LOAD_RETIRED.*
MEM_LOAD_L3_HIT_RETIRED.*
```

, where `.*` means that all sub-events inside a group can be configured as precise events.

In IBS sampling, whenever overflow occurs, IBS saves the instruction causing the overflow into a buffer which is then read by the interrupt handler. This capability of IBS makes it precise. 

uProf and Linux perf support IBS sampling. Perf supports two-levels of precision.

The TMA methodology heavily relies on precise events to locate the source of inefficient execution of the code. An example of using precise events to mitigate skid can be found on the [easyperf blog](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid)[^2]. Users of Linux `perf` should add `ppp` suffix to the event to enable precise tagging:

```bash
$ perf record -e cycles:ppp -- ./a.exe
```

### Analyzing Memory Accesses {#sec:sec_PEBS_DLA}

Memory accesses are a critical factor for the performance of many applications. With PEBS, it is possible to gather detailed information about memory accesses in the program. The feature that allows this to happen is called Data Address Profiling. To provide additional information about sampled loads and stores, it leverages the following fields inside the PEBS facility (see Figure @fig:PEBS_record):

* Data Linear Address (0x98)
* Data Source Encoding (0xA0)
* Latency value (0xA8)

If the performance event supports the Data Linear Address (DLA) facility, and DLA is enabled, the CPU will dump memory addresses and latency of the sampled memory access. Keep in mind; this feature does not trace all the stores and loads. Otherwise, the overhead would be too big. Instead, it samples on memory accesses, i.e., analyzes only one from 1000 accesses or so. You can customize how many sample per second you want.

One of the most important use cases for this PEBS extension is detecting True and False Sharing, which we will discuss in [@sec:TrueFalseSharing]. Linux `perf c2c` tool heavily relies on DLA data to find contested memory accesses, which could experience True/False sharing.

Also, with the help of Data Address Profiling, you can get general statistics for memory accesses in a program:

```bash
$ perf mem record -- ./a.exe
$ perf mem -t load report --sort=mem --stdio
# Samples: 656  of event 'cpu/mem-loads,ldlat=30/P'
# Total weight : 136578
# Overhead       Samples  Memory access
# ........  ............  ........................
    44.23%           267  LFB or LFB hit
    18.87%           111  L3 or L3 hit
    15.19%            78  Local RAM or RAM hit
    13.38%            77  L2 or L2 hit
     8.34%           123  L1 or L1 hit
```

From this output, we can see that 8% of the loads in the application were satisfied with L1 cache, 15% from DRAM, and so on.

[^1]: PEBS grabber tool - [https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber). Requires root access.
[^2]: Performance skid - [https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid).
[^4]: Hardware event skid - [https://software.intel.com/en-us/vtune-help-hardware-event-skid](https://software.intel.com/en-us/vtune-help-hardware-event-skid).
