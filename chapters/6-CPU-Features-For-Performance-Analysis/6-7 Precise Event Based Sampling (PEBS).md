---
typora-root-url: ..\..\img
---

[TODO]: rename to Hardware-Based Sampling?

## Processor Event-Based Sampling {#sec:secPEBS}

The Processor Event-Based Sampling (PEBS) is another very useful feature in CPUs that provides many different ways to enhance performance analysis. Similar to Last Branch Record (see [@sec:lbr]), PEBS is used while profiling the program to capture additional data with every collected sample. In Intel processors, the PEBS feature was introduced in NetBurst microarchitecture. A similar feature on AMD processors is called Instruction Based Sampling (IBS) and is available starting with the Family 10h generation of cores (code-named "Barcelona" and "Shanghai").

### PEBS on Intel Platforms

The set of additional data has a defined format, which is called the PEBS record. When a performance counter is configured for PEBS, the processor saves the contents of the PEBS buffer, which is later stored in memory. The record contains the architectural state of the processor, for instance, the state of the general-purpose registers (`EAX`, `EBX`, `ESP`, etc.), instruction pointer register (`EIP`), flags register (`EFLAGS`) and more. The content layout of a PEBS record varies across different implementations that support PEBS. See [@IntelOptimizationManual, Volume 3B, Chapter 18.6.2.4 Processor Event-Based Sampling (PEBS)] for details of enumerating PEBS record format. PEBS Record Format for Intel Skylake CPU is shown in Figure @fig:PEBS_record.

![PEBS Record Format for 6th Generation, 7th Generation and 8th Generation Intel Core Processor Families. *© Image from [@IntelOptimizationManual, Volume 3B, Chapter 18].*](../../img/pmu-features/PEBS_record.png){#fig:PEBS_record width=90%}

Users can check if PEBS is enabled by executing `dmesg`:

```bash
$ dmesg | grep PEBS
[    0.061116] Performance Events: PEBS fmt1+, IvyBridge events, 16-deep LBR, full-width counters, Intel PMU driver.
```

Linux `perf` doesn't export the raw PEBS output as it does for LBR.[^5] Instead, it processes PEBS records and extracts only the subset of data depending on a particular need. So, it's not possible to access the collection of raw PEBS records with Linux `perf`. However, Linux `perf` provides some PEBS data processed from raw samples, which can be accessed by `perf report -D`.  To dump raw PEBS records, one can use [`pebs-grabber`](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber)[^1] tool.

### IBS on AMD Platforms

### XXX on ARM Platforms

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

TMA methodology (see [@sec:TMA]) heavily relies on precise events to locate the source of inefficient execution of the code. An example of using precise events to mitigate skid can be found on [easyperf blog](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid)[^2]. Users of Linux `perf` should add `ppp` suffix to the event to enable precise tagging:

```bash
$ perf record -e cpu/event=0xd1,umask=0x20,name=MEM_LOAD_RETIRED.L3_MISS/ppp -- ./a.exe
```

### Lower Sampling Overhead

Frequently generating interrupts and having an analysis tool itself capture program state inside the interrupt service routine is very costly since it involves OS interaction. This is why some hardware allows automatically sampling multiple times to a dedicated buffer without any interrupts. Only when the dedicated buffer is full, the processor raises an interrupt, and the buffer gets flushed to memory. This has a lower overhead than traditional interrupt-based sampling. 

When a performance counter is configured for PEBS, an overflow condition in the counter will arm the PEBS mechanism. On the subsequent event following overflow, the processor will generate a PEBS event. On a PEBS event, the processor stores the PEBS record in the PEBS buffer area, clears the counter overflow status and reloads the counter with the initial value. If the buffer is full, the CPU will raise an interrupt. [@IntelOptimizationManual, Volume 3B, Chapter 18]

Note that the PEBS buffer itself is located in the main memory, and its size is configurable. Again, it is the job of a performance analysis tool to allocate and configure the memory area for the CPU to be able to dump PEBS records in it. 

### Analyzing Memory Accesses {#sec:sec_PEBS_DLA}

Memory accesses are a critical factor for the performance of many applications. With PEBS, it is possible to gather detailed information about memory accesses in the program. The feature that allows this to happen is called Data Address Profiling. To provide additional information about sampled loads and stores, it leverages the following fields inside the PEBS facility (see Figure @fig:PEBS_record):

* Data Linear Address (0x98)
* Data Source Encoding (0xA0)
* Latency value (0xA8)

If the performance event supports the Data Linear Address (DLA) facility, and DLA is enabled, the CPU will dump memory addresses and latency of the sampled memory access. Keep in mind; this feature does not trace all the stores and loads. Otherwise, the overhead would be too big. Instead, it samples on memory accesses, i.e., analyzes only one from 1000 accesses or so. You can customize how many sample per second you want.

One of the most important use cases for this PEBS extension is detecting [True/False sharing](https://en.wikipedia.org/wiki/False_sharing),[^3] which we will discuss in [@sec:TrueFalseSharing]. Linux `perf c2c` tool heavily relies on DLA data to find contested memory accesses, which could experience True/False sharing.

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
[^3]: False sharing - [https://en.wikipedia.org/wiki/False_sharing](https://en.wikipedia.org/wiki/False_sharing).
[^4]: Hardware event skid - [https://software.intel.com/en-us/vtune-help-hardware-event-skid](https://software.intel.com/en-us/vtune-help-hardware-event-skid).
[^5]: For LBR, Linux perf dumps entire contents of LBR stack with every collected sample. So, it's possible to analyze raw LBR dumps collected by Linux perf.
