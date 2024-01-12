## Sensitivity to Last Level Cache {#sec:Sensitivity2LLC}

Processors have an increasing number of cores and execution threads. For instance, AMD integrates up to 128 cores capable of executing 256 threads in its Genoa microarchitecture. This trend causes shared resources such as last-level cache (LLC) and off-chip memory bandwidth to come under increased pressure. Therefore, they must be scaled and/or managed as best as possible.

Recent commercial processors such as Intel Xeon [@QoSXeon], ARM ThunderX [@QoSThunderX], or AMD EPYC  include hardware support for users to control the allocation of both LLC space and memory bandwidth to processor threads. In this way, each thread can only use its allocated amount of shared resources, which helps to reduce interference with other threads.

In this section we will characterize the shared cache usage of an AMD Milan processor running single-threaded memory intensive benchmarks of SPEC CPU2017. Our analysis will allow us to identify three different types of applications according to their use of the LLC. This result can be applied to properly size the processor LLC, especially considering the wide range available on the market. For example, we can determine whether an application could benefit from a larger LLC, i.e., whether an investment in new hardware would be justified. Or conversely, if an application has enough with a tight cache size and therefore we can buy a cheaper processor.

### AMD Milan Core Organization

AMD launched in 2021 its AMD EPYC 7003 Series Processors, a processor family targeting the high-performance server segment. These processors are composed of Zen 3 cores, code-named Milan [@amd_milan].

For this study, we have used a server with a 16-core AMD EPYC 7313P processor. The main characteristics of this system are specified in table @tbl:experimental_setup.

----------------------------------------------------------------------------
 Feature               Value
----------------       ----------------------------------------------------
 Processor             AMD EPYC 7313P

 Cores x threads       16 $\times$ 2
 
 Configuration         4 CCX $\times$ 4 cores/CCX
 
 Frequency             3.0/3.7 GHz, base/max

 L1 cache (I, D)       8-ways, 32 KiB (per core)

 L2 cache              8-ways, 512 KiB (per core)

 LLC                   16-ways, 32 MiB, non-inclusive (per CCX)
 
 Main Memory           512 GiB DDR4, 8 channels, nominal peak BW: 204.8 GB/s,

 TurboBoost            Disabled

 Hyperthreading        Disabled (1 thread/core)

 OS                    Ubuntu 22.04, kernel 5.15.0-76

----------------------------------------------------------------------------

Table: Main features of the server used in the experiments. {#tbl:experimental_setup}

The 7313P processor consists of four Core Complex Dies (CCDs) connected to each other and to off-chip memory via an I/O chiplet (see figure @fig:milan7313P). Each CCD integrates a Core CompleX (CCX) and an I/O connection. In turn, each CCX has four Zen3 cores capable of executing eight threads that share a 32 MiB victim LLC, i.e., the LLC is filled with the cache blocks evicted from the four L2 caches of a CCX. Recent processors such as ARM Neoverse and Intel Skylake-SP also implement this mostly-exclusive content management. Although there is a total of 128 MiB of LLC, the four cores of a CCX cannot store cache blocks in an LLC other than their own 32 MiB LLC (32 MiB/CCX x 4 CCX).

![AMD Milan 7313P clustered memory hierarchy. This processor is a multichip module with five dies: one I/O die and four Core Complex Dies (CCDs) with a total of 16 cores. On each CCD there is a Core CompleX (CCX) with four 2-SMT Zen3 cores (2SMT C) sharing a 32 MiB LLC.](../../img/other-tuning/Milan7313P.png){#fig:milan7313P width=90%}

## Monitoring & Control Tools

To characterize the applications we use hardware counters. Hardware counters record events that occur during the execution of an application (see section {@sec:PMU}), for example, retired instructions, elapsed cycles, or misses experienced in the LLC. Hardware counters can be configured and read through the model-specific registers (MSR) [@amd_ppr]. The configuration consists of specifying the event to be monitored and how it will be monitored[^1]. In our system, this is done by writing to a `PERF_CTL[0-5]` register (MSR `0xC001020[0,2,4,6,8,A]`). The `PERF_CTR[0-5]` registers (MSR `0xC001020[1,3,5,7,9,B]`) are the counters associated to the previous control registers. For example, for counter 0 to register the number of instructions retired from an application running in thread 1, the following command is executed:

```bash
$ wrmsr -p 1 0xC0010200 0x5100C0
```

where `-p 1` refers to the hardware thread 1, `0xC0010200` is the MSR for the control of counter 0 (`PERF_CTL[0]`), and `0x5100C0` specifies the identifier of the event to be measured (retired instructions, `PMCx0C0`) and the way in which it will be measured (user events ...).

Once the configuration is done, the following command is executed to read counter 0:

```bash
$ rdmsr -p 1 0xC0010201
```

where `-p 1` refers to the hardware thread 1 and `0xC0010201` is the MSR to read (`PERF_CTR[0]`).

In addition, there are specific banks of MSRs registers, belonging to _AMD64 Technology Platform Quality of Service Extensions_ (AMD QoSE) [@QoSAMD] that are used to monitor and enforce limits on LLC allocation and memory _read_ bandwidth per thread.

Specifically, to monitor LLC usage, first a resource management identifier (RMID), and a class of service (COS) are associated to a thread or group of threads[^2]. Then the monitoring identifier RMID and the event associated with the LLC monitoring (L3 Cache Occupancy Monitoring, `evtID 0x1`) are written to the `QM_EVTSEL` control register (MSR `0xC8D`). Finally, the `QM_CTR` register (MSR `0xC8E`) is read. For example, if we want to monitor the use of the LLC by the hardware thread 1:

```bash
# write PQR_ASSOC (MSR 0xC8F): RMID=1, COS=2 -> (COS << 32) + RMID
$ wrmsr -p 1 0xC8F 0x200000001

# write QM_EVTSEL (MSR 0xC8D): RMID=1, evtID=1 -> (RMID << 32) + evtID
$ wrmsr -p 1 0xC8D 0x100000001

# Read QM_CTR (MSR 0xC8E)
$ rdmsr -p 1 0xC8E 
```

To obtain the estimate of the LLC usage measured in bytes, we have to multiply the value returned by this reading by the cache line size.[^7]

LLC space management is performed by writing to a 16-bit per-thread binary mask. Each bit of the mask allows a thread to use a given sixteenth fraction of the LLC (1/16 = 2 MiB in the case of the AMD Milan 7313P). Multiple threads can use the same fraction(s), implying a competitive shared use of the same subset of LLC.

To set limits, assuming that there is already an assignment of RMID and COS to a thread (`wrmsr -p 1 0xC8F 0x200000001`), we have to write in the `L3_MASK_n` register, where `n` is the COS, the cache partitions that can be used by the corresponding COS. For example, to limit to thread 1 the available space in the LLC to half of the total space[^3]:

```bash
# this command requires root access
# write L3_MASK_2 (MSR 0xC92): 0x00FF (half of the LLC space)
$ wrmsr -p 1 0xC92 0x00FF
```

Similarly, the memory _read_ bandwidth allocated to a thread can be limited. This is achieved by writing an unsigned integer to a specific MSR register, which sets a maximum read bandwidth in 1/8 GB/s increments.

## Workload: SPEC CPU2017

We use a subset of benchmarks from the SPEC CPU2017 suite[^4]. Specifically, we selected the 33 memory-intensive single-threaded applications suggested in [@MemCharacterizationSPEC2006]. These applications have been compiled with the version of GCC and the base flags specified by SPEC in the configuration file provided with the suite. Specifically, version 6.3.1 has been used, and the following options: `-g -O3 -march=native -fno-unsafe-math-optimizations -fno-tree-loop-vectorize`. `-DBIG_MEMORY` has been used for `deepsjeng` and `-m64` when required. SPEC CPU2017 contains a collection of industry-standardized performance benchmarks that stress the processor, memory subsystem and compiler. It is widely used to compare the performance of high-performance systems[^5]. It is also extensively used in computer architecture research. 

The methodology is detailed in [@Navarro-Torres2023]. The code and the information necessary to reproduce the experiments can be found in the following public repository: <https://github.com/agusnt/BALANCER>.

## Metrics 

The ultimate metric for quantifying the performance of an application is execution time. Other metrics, such as cache miss rates, are used to analyze the influence of the memory hierarchy on system performance. In our case, we will characterize applications with these three metrics: 1) CPI, cycles per instruction[^6], 2) DMPKI, demand misses in the LLC per thousand instructions, and 3) MPKI, total misses (demand + prefetch) in the LLC per thousand instructions.

Table @tbl:metrics shows the formulas used to calculate each metric from specific hardware counters.

-----------------------------------
Metric   Formula                   
------   --------------------------
CPI      PMCx076 / PMCx0C0 

DMPKI    PMCx043 / (PMCx0C0 / 1000)

MPKI     L3PMCx04 / (PMCx0C0 / 1000)

------------------------------------

Table: Metrics calculation from hardware counters [@amd_ppr][@QoSAMD]. {#tbl:metrics}

## Performance vs. LLC Capacity

In this section we are going to characterize the behavior of applications *running alone* when their allocated space in the LLC changes from 0 to 32 MiB with 2 MiB steps.

Figure @fig:characterization_llc shows in graphs, from left to right, CPI, DMPKI and MPKI for each assigned LLC size. Three lines corresponding to `503.bwaves` (blue), `520.omnetpp` (green) and `554.roms` (red), representative of the three main trends observed in all applications, are represented in each graph.

![CPI, DMPKI, and MPKI for increasing LLC allocation limits (2 MiB steps).](../../img/other-tuning/llc-bw.png){#fig:characterization_llc width=90%}

Two behaviors can be distinguished in the CPI and DMPKI graphs. On the one hand, `520.omnetpp` takes advantage of its available space in the LLC: both CPI and DMPKI decrease significantly as the space allocated in the LLC increases.  We can say that the behavior of `520.omnetpp` is sensitive to the size available in the LLC. Increasing the allocated LLC space improves performance because it avoids evicting cache lines that will be used in the future.

In contrast, `503.bwaves` and `554.roms` waste the space they occupy in the LLC. Both metrics remain virtually constant as the allocation limit in the LLC expands. We would say that the performance of these two applications is insensitive to their available space in the LLC. If our applications show this behavior, we can select a processor with a tight LLC size.

Let us now analyze the MPKI graph, the miss rate that considers both processor and prefetch requests. First of all we can see that the MPKI values are always much higher than the DMPKI values. That is, most of the blocks are loaded from memory into the on-chip hierarchy by the prefetcher. This behavior is due to the fact that the prefetcher is efficient in preloading the private caches with the data to be used, thus eliminating most of the demand misses.

Regarding the variation of MPKI as the available space in the LLC changes, we observe that `520.omnetpp` and `503.bwaves` maintain the same behavior as in the CPI and DMPKI plots, `503.bwaves` remains constant while `520.omnetpp` decreases as the available space increases. However, MPKI shows a large decrease in `554.roms` as the available space increases while CPI and DMPKI remained virtually unchanged. In this case, the prefetcher is able to do its job, to eliminate demand misses, regardless of the available space in the LLC. However, as the available space decreases, the probability that the prefetcher will not find the blocks in the LLC and will have to load them from memory increases. Consequently, giving more LLC capacity to this type of applications does not directly benefit them, since it does not reduces its CPI, but it does benefit the system, since it reduces memory traffic.  

Although it may not seem intuitive in view of the CPI and MPKI figures, the analysis of the MPKI metric leads us to consider applications that behave as `554.roms` as cache sensitive and, therefore, it seems a good idea not to limit their available LLC space so as not to increase bandwidth consumption.
Higher bandwidth consumption may increase memory access latency, which in turn implies a performance degradation of all applications running on the system [@Navarro-Torres2023].

\highlight{The MPKI metric allows quantifying the benefit associated with LLC occupancy more comprehensively than CPI or DMPKI, which are the commonly used metrics. The variation of CPI or DMPKI only reflects the benefit that affects the application itself, while MPKI additionally reflects the benefit that is achieved for the system.}

[^1]: Preliminary Processor Programming Reference (PPR) for AMD Family 19h Model 01h, Revision B1 Processors, volume 1.
[^2]: AMD64 Technology Platform Quality of Service Extensions.
[^3]: Class Of Service (COS) in AMD terminology.
[^4]: SPEC CPU® 2017 - [https://www.spec.org/cpu2017/](https://www.spec.org/cpu2017/).
[^5]: SPEC CPU2017 Results: [https://www.spec.org/cpu2017/results/](https://www.spec.org/cpu2017/results/)
[^6]: We use CPI instead of time per instruction since we assume that the CPU frequency does not change during the experiments.
[^7]: AMD documentation [@QoSAMD] rather uses the term L3 Cache Conversion Factor, which can be determined with the `cpuid` instruction.
