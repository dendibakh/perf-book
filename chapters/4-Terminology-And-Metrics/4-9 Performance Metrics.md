## Performance Metrics {#sec:PerfMetrics}

In addition to the performance events that we discussed earlier in this chapter, performance engineers frequently use metrics, which are built on top of raw events. Table {@tbl:perf_metrics} shows a list of metrics for Intel's 12th-gen Goldencove architecture along with descriptions and formulas. The list is not exhaustive, but it shows the most important metrics. Complete list of metrics for Intel CPUs and their formulas can be found in [TMA_metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx)[^1]. The last section in this chapter shows how performance metrics can be used in practice.

--------------------------------------------------------------------------
Metric  Description                   Formula
Name           
------- -------------------------- ---------------------------------------
L1MPKI  L1 cache true misses       1000 * MEM_LOAD_RETIRED.L1_MISS_PS /
        per kilo instruction for   INST_RETIRED.ANY
        retired demand loads.      

L2MPKI  L2 cache true misses       1000 * MEM_LOAD_RETIRED.L2_MISS_PS /
        per kilo instruction for   INST_RETIRED.ANY
        retired demand loads.      

L3MPKI  L3 cache true misses       1000 * MEM_LOAD_RETIRED.L3_MISS_PS /
        per kilo instruction for   INST_RETIRED.ANY
        retired demand loads.                

Branch  Ratio of all branches      BR_MISP_RETIRED.ALL_BRANCHES / 
Mispr.  which mispredict           BR_INST_RETIRED.ALL_BRANCHES
Ratio  

Code    STLB (2nd level TLB) code  1000 * ITLB_MISSES.WALK_COMPLETED 
STLB    speculative misses per     / INST_RETIRED.ANY
MPKI    kilo instruction (misses 
        of any page-size that 
        complete the page walk)

Load    STLB data load             1000 * DTLB_LOAD_MISSES.WALK_COMPLETED 
STLB    speculative misses         / INST_RETIRED.ANY
MPKI    per kilo instruction

Store   STLB data store            1000 * DTLB_STORE_MISSES.WALK_COMPLETED 
STLB    speculative misses         / INST_RETIRED.ANY
MPKI    per kilo instruction

Load    Actual Average Latency for L1D_PEND_MISS.PENDING / 
Miss    L1 data-cache miss demand  MEM_LOAD_COMPLETED.L1_MISS_ANY
Real    load operations 
Latency (in core cycles)

ILP     Instr.-Level-Parallelism   UOPS_EXECUTED.THREAD / 
        per-core (average number   UOPS_EXECUTED.CORE_CYCLES_GE_1,
        of μops executed when      divide by 2 if SMT is enabled
        there is execution) 

MLP     Memory-Level-Parallelism   L1D_PEND_MISS.PENDING / 
        per-thread (average number L1D_PEND_MISS.PENDING_CYCLES
        of L1 miss demand load 
        when there is at least one
        such miss.)

DRAM    Average external Memory    ( 64 * ( UNC_M_CAS_COUNT.RD + 
BW Use  Bandwidth Use for reads             UNC_M_CAS_COUNT.WR ) 
GB/sec  and writes                 / 1GB ) / Time

IpCall  Instructions per near call INST_RETIRED.ANY / 
        (lower number means higher BR_INST_RETIRED.NEAR_CALL
        occurrence rate)

Ip      Instructions per Branch    INST_RETIRED.ANY / 
Branch                             BR_INST_RETIRED.ALL_BRANCHES

IpLoad  Instructions per Load      INST_RETIRED.ANY / 
                                   MEM_INST_RETIRED.ALL_LOADS_PS

IpStore Instructions per Store     INST_RETIRED.ANY / 
                                   MEM_INST_RETIRED.ALL_STORES_PS

IpMisp  Number of Instructions per INST_RETIRED.ANY / 
redict  non-speculative Branch     BR_MISP_RETIRED.ALL_BRANCHES
        Misprediction

IpFLOP  Instructions per FP        See TMA_metrics.xlsx
        (Floating Point) operation 

IpArith Instructions per FP        See TMA_metrics.xlsx
        Arithmetic instruction
                
IpArith Instructions per FP Arith. INST_RETIRED.ANY / 
Scalar  Scalar Single-Precision    FP_ARITH_INST_RETIRED.SCALAR_SINGLE
SP      instruction 

IpArith Instructions per FP Arith. INST_RETIRED.ANY / 
Scalar  Scalar Double-Precision    FP_ARITH_INST_RETIRED.SCALAR_DOUBLE
DP      instruction 

Ip      Instructions per FP        INST_RETIRED.ANY / (
Arith   Arithmetic AVX/SSE         FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE+
AVX128  128-bit instruction        FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE)

Ip      Instructions per FP        INST_RETIRED.ANY / ( 
Arith   Arithmetic AVX*            FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE+
AVX256  256-bit instruction        FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE)

Ip      Instructions per SW        INST_RETIRED.ANY / 
SWPF    prefetch instruction       SW_PREFETCH_ACCESS.T0:u0xF
        (of any type)
--------------------------------------------------------------------------

Table: A list (not exhaustive) of secondary metrics along with descriptions and formulas for Intel Goldencove architecture. {#tbl:perf_metrics}

A few notes on those metrics. First, ILP and MLP metrics do not represent theoretical maximums for an application, rather they measure ILP and MLP on a given machine. On an ideal machine with infinite resources numbers will be higher. Second, all metrics besides "DRAM BW Use" and "Load Miss Real Latency" are fractions; we can apply fairly straightforward reasoning to each of them to tell whether a specific metric is high or low. But to make sense of "DRAM BW Use" and "Load Miss Real Latency" metrics, we need to put it in a context. For the former, we would like to know if a program saturates the memory bandwidth or not. The latter gives you an idea for the average cost of a cache miss, which is useless by itself unless you know the latencies of the cache hierarchy. We will discuss how to find out cache latencies and peak memory bandwidth in the next section.

Formulas in the table give an intuition on how performance metrics are calculated, so that you can build similar metrics on another platform as long as underlying performance events are available there. Some tools can report performance metrics automatically. If not, you can always calculate those metrics manually since you know the formulas and corresponding performance events that must be collected.

[^1]: TMA metrics - [https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx).