## Secondary Metrics {#sec:SecondaryMetrics}

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
        of uops executed when      divide by 2 if SMT is enabled
        there is execution) 

MLP     Memory-Level-Parallelism   L1D_PEND_MISS.PENDING / 
        per-thread (average number L1D_PEND_MISS.PENDING_CYCLES
        of L1 miss demand load 
        when there is at least one
        such miss.)

DRAM    Average external Memory    ( 64 * ( UNC_M_CAS_COUNT.RD + 
BW Use  Bandwidth Use for reads             UNC_M_CAS_COUNT.WR ) 
GB/sec and writes                 / 1GB ) / Time

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

Table: Secondary metrics. {#tbl:secondary_metrics}


DRAM BW Use formula: 64, because it's the size of the cache line