---
typora-root-url: ..\..\img
---

## Hardware-Based Sampling Features

Major CPU vendors provide a set of additional features to enhance performance analysis. Since CPU vendors approach performance monitoring in different ways, those capabilities vary in not only how they are called but also what you can do with them. In Intel processors, it is called Processor Event-Based Sampling (PEBS), first introduced in NetBurst microarchitecture. A similar feature on AMD processors is called Instruction Based Sampling (IBS) and is available starting with the AMD Opteron Family (10h generation) of cores. Next we will discuss those features in more details, including their similarities and differences.

### PEBS on Intel Platforms

Similar to Last Branch Record, PEBS is used while profiling the program to capture additional data with every collected sample. When a performance counter is configured for PEBS, the processor saves the set of additional data, which has a defined format and is called the PEBS record. The format of a PEBS record for Intel Skylake CPU is shown in Figure @fig:PEBS_record. The record contains the state of general-purpose registers (`EAX`, `EBX`, `ESP`, etc.), `EventingIP`, `Data Linear Address`, and `Latency value`, which will discuss later. The content layout of a PEBS record varies across different microarchitectures, see [@IntelOptimizationManual, Volume 3B, Chapter 20 Performance Monitoring].

![PEBS Record Format for 6th Generation, 7th Generation and 8th Generation Intel Core Processor Families. *© Image from [@IntelOptimizationManual, Volume 3B, Chapter 20].*](../../img/pmu-features/PEBS_record.png){#fig:PEBS_record width=100%}

Since Skylake, the PEBS record has been enhanced to collect XMM registers and LBR records. The format has been restructured where fields are grouped into Basic group, Memory group, GPR group, XMM group, and LBR group. Performance profiling tools have the option to select data groups of interest and thus reduce the record size in memory and record generation latency. By default, the PEBS record will only contain the Basic group.

One of the notable benefits of using PEBS is lower sampling overhead compared to a regular interrupt-based sampling. Recall that when the counter overflows, the CPU generates an interrupt to collect one sample. Frequently generating interrupts and having an analysis tool itself capture program state inside the interrupt service routine is very costly since it involves OS interaction. 

On the other hand, PEBS keeps a buffer to temporarily store multiple PEBS records. Suppose, we are sampling on load events using PEBS. When a performance counter is configured for PEBS, an overflow condition in the counter will not trigger an interrupt, instead it will arm the PEBS mechanism. The mechanism will then trap the next load, capture a new record and store it in the dedicated PEBS buffer area. The mechanism also takes care of clearing the counter overflow status and reloading the counter with the initial value. Only when the dedicated buffer is full, the processor raises an interrupt, and the buffer gets flushed to memory. This mechanism lowers the sampling overhead by triggering much fewer interrupts.

Linux users can check if PEBS is enabled by executing `dmesg`:

```bash
$ dmesg | grep PEBS
[    0.113779] Performance Events: XSAVE Architectural LBR, PEBS fmt4+-baseline,  
AnyThread deprecated, Alderlake Hybrid events, 32-deep LBR, full-width counters, Intel PMU driver.
```

For LBR, Linux perf dumps entire contents of LBR stack with every collected sample. So, it is possible to analyze raw LBR dumps collected by Linux perf. However, for PEBS, Linux `perf` doesn't export the raw output as it does for LBR. Instead, it processes PEBS records and extracts only the subset of data depending on a particular need. So, it's not possible to access the collection of raw PEBS records with Linux `perf`. However, Linux `perf` provides some PEBS data processed from raw samples, which can be accessed by `perf report -D`. To dump raw PEBS records, one can use [`pebs-grabber`](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber)[^1] tool.

### IBS on AMD Platforms

Instruction-Based Sampling (IBS) is an AMD64 processor feature that can be used to collect specific metrics related to instruction fetch and instruction execution. The processor pipeline of an AMD processor consists of two separate phases: a front-end phase that fetches AMD64 instruction bytes and a back-end phase that executes `ops`. As the phases are logically separated, there are two independent sampling mechanisms: IBS Fetch and IBS Execute. 

- IBS Fetch monitors the front-end of the pipeline and provides information about ITLB (hit or miss), I-cache (hit or miss), fetch address, fetch latency and a few other things.
- IBS Execute monitors the back-end of the pipeline and provides information about instruction execution behavior by tracking the execution of a single op. For example: branch (taken or not, predicted or not), load/store (hit or miss in D-caches and DTLB, linear address, load latency).

There is a number of important differences between PMC and IBS in AMD processors. PMC counters are programmable, whereas IBS acts like fixed counters. IBS counters can only be enabled or disabled for monitoring, they can't be programmed to any selective events. IBS Fetch and Execute counters can be enabled/disabled independently. With PMC, user has to decide what events to monitor ahead of time. With IBS, a rich set of data is collected for each sampled instruction and then it is up to the user to analyze parts of the data they are interested in. IBS selects and tags an instruction to be monitored and then captures microarchitectural events caused by this instruction during its execution. A more detailed comparison of Intel PEBS and AMD IBS can be found in [@ComparisonPEBSIBS].

Since IBS is integrated into the processor pipeline and acts as a fixed event counter, the sample collection overhead is minimal. Profilers are required to process the IBS generated data, which could be huge in size depending upon sampling interval, number of threads configured, whether Fetch/Execute configured, etc. Until Linux kernel version 6.1, IBS always collects samples for all the cores. This limitation causes huge data collection and processing overhead. From Kernel 6.2 onwards, Linux perf supports IBS sample collection only for the configured cores. 

IBS is supported by Linux perf and the AMD uProf profiler. Here are sample commands to collect IBS Execute and Fetch samples:

```bash
$ perf record -a -e ibs_op/cnt_ctl=1,l3missonly=0/ -- benchmark.exe
$ perf record -a -e ibs_fetch/l3missonly=1/ -- benchmark.exe
$ perf report
```

where `cnt_ctl=0` counts clock cycles, `cnt_ctl=1` counts dispatched ops for an interval period; `l3missonly=1` only keeps the samples that had an L3 miss. These two parameters and a few other are described in more details in [@AMDUprofManual, Table 25. AMDuProfCLI Collect Command Options]. Note that in both of the commands above, `-a` option is used to collect IBS samples for all cores, otherwise `perf` would fail to collect samples on Linux kernel 6.1 or older. From the version 6.2 onwards, `-a` option is no longer needed unless you want to collect IBS samples for all cores. The `perf report` command will show samples attributed to functions and source code lines similar to regular PMU events but with added features that we will discuss later. AMD uProf command line tool can generate IBS raw data, which later can be converted to a CSV file for later postprocessing with MS Excel as described in [@AMDUprofManual, Section 7.10 ASCII Dump of IBS Samples].

### SPE on ARM Platforms

The Arm Statistical Profiling Extension (SPE) is an architectural feature designed for enhanced instruction execution profiling within Arm CPUs. The SPE feature extension is specified as part of Armv8-A architecture, with support from Arm v8.2 onwards. ARM SPE extension is architecturally optional, which means that ARM processor vendors are not required to implement it. ARM Neoverse cores support SPE since Neoverse N1 cores, introduced in 2019. 

Compared to other solutions, SPE is more similar to AMD IBS than it is to Intel PEBS. Similar to IBS, SPE is separate from the general performance monitor counters (PMC), but instead of two flavors of IBS (fetch and execute), there is just a single mechanism.

The SPE sampling process is built in as part of the instruction execution pipeline. Sample collection is still based on a configurable interval, but operations are statistically selected. Each sampled operation generates a sample record, which contains various data about execution of this operation. SPE record saves address of the instruction, virtual and physical address for the data accessed by loads and stores, the source of the data access (cache or DRAM) and timestamp to correlate with other events in the system. Also, it can give latency of various pipeline stages, such as Issue latency (from dispatch to execution), Translation latency (cycle count for a virtual-to-physical address translation) and Execution latency (latency of load/stores in the functional unit). The whitepaper [@ARMSPE] describes ARM SPE in more details as well as shows a few optimization examples using it.

Similar to Intel PEBS and AMD IBS, ARM SPE helps to reduce the sampling overhead and enables longer collections. In addition to that, it supports post-filtering of sample records, which helps to reduce the memory required for storage. 

[TODO]: Linux perf driver for arm_spe should be installed first
https://developer.arm.com/documentation/ka005362/latest/
On Amazon Linux 2 and 2023, the SPE PMU is available by default on Graviton metal instances, you can check for its existence by verifying:
https://github.com/aws/aws-graviton-getting-started/blob/main/perfrunbook/debug_hw_perf.md#capturing-statistical-profiling-extension-spe-hardware-events-on-graviton-metal-instances
```$ sudo apt install linux-modules-extra-$(uname -r)```

SPE profiling is enabled in the Linux `perf` tool and can be used as follows:

```bash
$ perf record -e arm_spe_0/<controls>/ -- test_program
$ perf report --stdio
$ spe-parser perf.data -t csv
```

, where `<controls>` lets you optionally specify various controls and filters for the collection. `perf report` will give the usual output according to what user asked for with `<controls>` options. `spe-parser`[^5] is a tool developed by ARM engineers to parse the captured perf record data and save all the SPE records into a CSV file.

[TODO]: Is it possible to use SPE on Windows on ARM? Can `WindowsPerf` collect SPE data that can be parsed by `spe-parser`?
Not yet. ETA: September 2024

### Precise Events

Now that we covered the advanced sampling features, let's discuss **how** they can be used to improve performance analysis. We will start with the notion of precise events.

One of the major problems in profiling is pinpointing the exact instruction that caused a particular performance event. As discussed in [@sec:profiling], interrupt-based sampling is based on counting a specific performance event and waiting until it overflows. When an overflow interrupt happens, it takes a processor some time to stop the execution and tag the instruction that caused the overflow. This is especially difficult for modern complex out-of-order CPU architectures.

It introduces the notion of a skid, which is defined as the distance between the IP (instruction address) that caused the event to the IP where the event is tagged. Skid makes it difficult to discover the instruction causing the performance issue. Consider an application with a big number of cache misses and the hot assembly code that looks like this:

```asm
; load1 
; load2
; load3
```

The profiler might tag `load3` as the instruction that causes a large number of cache misses, while in reality, `load1` is the instruction to blame. For high-performance processors, this skid can be hundreds of processor instructions. This usually causes a lot of confusion for performance engineers. Interested readers could learn more about underlying reasons for such issues on [Intel Developer Zone website](https://software.intel.com/en-us/vtune-help-hardware-event-skid)[^4].

The problem with the skid is mitigated by having the processor itself store the instruction pointer (along with other information). With Intel PEBS, the `EventingIP` field in the PEBS record indicates the instruction that caused the event. This is typically available only for a subset of supported events, called "Precise Events". A complete list of precise events for specific microarchitecture can be found in [@IntelOptimizationManual, Volume 3B, Chapter 20 Performance Monitoring]. An example of using PEBS precise events to mitigate skid can be found on the [easyperf blog](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid).[^2]

Listed below are precise events for the Intel Skylake Microarchitecture:

```
INST_RETIRED.*        OTHER_ASSISTS.*    BR_INST_RETIRED.*     BR_MISP_RETIRED.*
FRONTEND_RETIRED.*    HLE_RETIRED.*      RTM_RETIRED.*         MEM_INST_RETIRED.*
MEM_LOAD_RETIRED.*    MEM_LOAD_L3_HIT_RETIRED.*
```

, where `.*` means that all sub-events inside a group can be configured as precise events.

With AMD IBS and ARM SPE, all the collected samples are precise by design since the HW captures the exact instruction address. In fact, they both work in a very similar fashion. Whenever an overflow occurs, the mechanism saves the instruction causing the overflow into a dedicated buffer which is then read by the interrupt handler. As the address is preserved, IBS and SPE samples attribution to the instructions are precise.

Users of Linux `perf` on Intel and AMD platforms must add `pp` suffix to one of the events listed above to enable precise tagging as shown below. However, on ARM platforms, it has no effect, so users must use the `arm_spe_0` event.

```bash
$ perf record -e cycles:pp -- ./a.exe
```

[TODO]: For Denis: show example of regular vs. precise events?

Precise events provide a relief for performance engineers as they help to avoid misleading data that often confuses beginners and even senior developers. The TMA methodology heavily relies on precise events to locate the exact line of source code where the inefficient execution takes place.

### Analyzing Memory Accesses {#sec:sec_PEBS_DLA}

Memory accesses are a critical factor for the performance of many applications. Both PEBS and IBS enable gathering detailed information about memory accesses in a program. For instance, you can not only sample loads, but also collect their target addresses and access latency. Keep in mind; this does not trace all the stores and loads. Otherwise, the overhead would be too big. Instead, it analyzes only one out of 100'000 accesses or so. You can customize how many sample per second you want. With large enough collection of samples it can give an accurate statistical picture of the memory accesses.

In PEBS, the feature that allows this to happen is called Data Address Profiling (DLA). To provide additional information about sampled loads and stores, it uses the `Data Linear Address` and `Latency Value` fields inside the PEBS facility (see Figure @fig:PEBS_record). If the performance event supports the DLA facility, and DLA is enabled, the processor will dump the memory address and latency of the sampled memory access. You can also filter memory accesses that have latency higher than a certain threshold. This is useful for finding long-latency memory accesses, which can be a performance bottleneck for many applications.

With the IBS Execute and ARM SPE sampling, you can also do in-depth analysis of memory accesses performed by an application. One approach is to dump collected samples and process them manually. IBS saves the exact linear address, its latency, where the access was served from (cache or DRAM), and whether it hit or missed in the DTLB. SPE can be used to estimate latency and bandwidth of the memory subsystem components, estimate memory latencies of individual loads/stores, and more.

[TODO]: refer to section that shows using `perf mem` in Chapter 8 as an example of using PEBS/IBS/SPE features.

One of the most important use cases for these extensions is detecting True and False Sharing, which we will discuss in [@sec:TrueFalseSharing]. The Linux `perf c2c` tool heavily relies on all three mechanisms (PEBS, IBS and SPE) to find contested memory accesses, which could experience True/False sharing: it matches load/store addresses for different threads and checks if the hit occurs in a cache line modified by other threads.

[^1]: PEBS grabber tool - [https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber). Requires root access.
[^2]: Performance skid - [https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid)
[^4]: Hardware event skid - [https://software.intel.com/en-us/vtune-help-hardware-event-skid](https://software.intel.com/en-us/vtune-help-hardware-event-skid)
[^5]: ARM SPE parser - [https://gitlab.arm.com/telemetry-solution/telemetry-solution](https://gitlab.arm.com/telemetry-solution/telemetry-solution)