## Secondary Metrics {#sec:SecondaryMetrics}

--------------------------------------------------------------------------
Metric  Units   Description                   Formula
 Name           
------ -------- --------------------- ---------------------------------------
L1MPKI Fraction L1 cache true misses   1000 * MEM_LOAD_RETIRED.L1_MISS_PS /
                per kilo instruction      INST_RETIRED.ANY
                for retired demand 
                loads.

L2MPKI Fraction L2 cache true misses   1000 * MEM_LOAD_RETIRED.L2_MISS_PS /
                per kilo instruction      INST_RETIRED.ANY
                for retired demand 
                loads.

L3MPKI Fraction L3 cache true misses   1000 * MEM_LOAD_RETIRED.L3_MISS_PS /
                per kilo instruction      INST_RETIRED.ANY
                for retired demand 
                loads.                

Branch  Fraction Ratio of all branches  BR_MISP_RETIRED.ALL_BRANCHES / 
Mispr.           which mispredict       BR_INST_RETIRED.ALL_BRANCHES
Ratio  

Code   Fraction STLB (2nd level TLB)   1000 * ITLB_MISSES.WALK_COMPLETED 
STLB            code speculative       / INST_RETIRED.ANY
MPKI            misses per kilo  
                instruction (misses 
                of any page-size that 
                complete the page 
                walk)

Load   Fraction STLB data load         1000 * DTLB_LOAD_MISSES.WALK_COMPLETED 
STLB            speculative misses     / INST_RETIRED.ANY
MPKI            per kilo instruction

Store  Fraction STLB data store        1000 * DTLB_STORE_MISSES.WALK_COMPLETED 
STLB            speculative misses     / INST_RETIRED.ANY
MPKI            per kilo instruction

Load   Fraction Actual Average Latency L1D_PEND_MISS.PENDING / 
Miss            for L1 data-cache miss MEM_LOAD_COMPLETED.L1_MISS_ANY
Real            demand load operations 
Lat.            (in core cycles)

ILP    Fraction Instruction-Level-     UOPS_EXECUTED.THREAD / 
                Parallelism per-core   UOPS_EXECUTED.CORE_CYCLES_GE_1,
                (average number of     divide by 2 if SMT is enabled
                uops executed when 
                there is execution) 

MLP    Fraction Memory-Level-          L1D_PEND_MISS.PENDING / 
                Parallelism per-thread L1D_PEND_MISS.PENDING_CYCLES
                (average number of L1 
                miss demand load when 
                there is at least one
                such miss.)

DRAM   GB/sec   Average external       ( 64 * ( UNC_M_CAS_COUNT.RD + 
BW Use          Memory Bandwidth Use            UNC_M_CAS_COUNT.WR ) 
                for reads and writes   / 1GB ) / Time

IpCall Fraction Instructions per       INST_RETIRED.ANY / 
                near call (lower       BR_INST_RETIRED.NEAR_CALL
                number means higher
                occurrence rate)

Ip     Fraction Instructions per       INST_RETIRED.ANY / 
Branch          Branch                 BR_INST_RETIRED.ALL_BRANCHES

IpLoad Fraction Instructions per Load  INST_RETIRED.ANY / 
                                       MEM_INST_RETIRED.ALL_LOADS_PS

Ip     Fraction Instructions per       INST_RETIRED.ANY / 
Store           Store                  MEM_INST_RETIRED.ALL_STORES_PS

IpMisp Fraction Number of Instructions INST_RETIRED.ANY / 
redict          per non-speculative    BR_MISP_RETIRED.ALL_BRANCHES
                Branch Misprediction

IpFLOP Fraction Instructions per FP    See TMA_metrics.xlsx
                (Floating Point) oper. 

Ip     Fraction Instructions per FP    See TMA_metrics.xlsx
Arith           Arithmetic instruction
                
Ip     Fraction Instructions per FP    INST_RETIRED.ANY / 
Arith           Arithmetic Scalar      FP_ARITH_INST_RETIRED.SCALAR_SINGLE
Scalar          Single-Precision 
SP              instruction 

Ip     Fraction Instructions per FP    INST_RETIRED.ANY / 
Arith           Arithmetic Scalar      FP_ARITH_INST_RETIRED.SCALAR_DOUBLE
Scalar          Double-Precision 
DP              instruction 

Ip     Fraction Instructions per FP    INST_RETIRED.ANY / (
Arith           Arithmetic AVX/SSE     FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE+
AVX128          128-bit instruction    FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE)

Ip     Fraction Instructions per FP    INST_RETIRED.ANY / ( 
Arith           Arithmetic AVX*        FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE+
AVX256          256-bit instruction    FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE)

Ip     Fraction Instructions per SW    INST_RETIRED.ANY / 
SWPF            prefetch instruction   SW_PREFETCH_ACCESS.T0:u0xF
                (of any type)
--------------------------------------------------------------------------

Table: Secondary metrics. {#tbl:secondary_metrics}

L1MPKI - L1 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L1_MISS_PS / INST_RETIRED.ANY`
L2MPKI - L2 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L2_MISS_PS / INST_RETIRED.ANY`
L3MPKI - L3 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L3_MISS_PS / INST_RETIRED.ANY`
Branch_Mispredict_Ratio - Ratio of all branches which mispredict
`BR_MISP_RETIRED.ALL_BRANCHES / BR_INST_RETIRED.ALL_BRANCHES`
Code_STLB_MPKI - 
`1000 * ITLB_MISSES.WALK_COMPLETED / INST_RETIRED.ANY`
Load_STLB_MPKI - STLB (2nd level TLB) data load speculative misses per kilo instruction (misses of any page-size that complete the page walk)
`1000 * DTLB_LOAD_MISSES.WALK_COMPLETED / INST_RETIRED.ANY`
Store_STLB_MPKI - STLB (2nd level TLB) data store speculative misses per kilo instruction (misses of any page-size that complete the page walk)
`1000 * DTLB_STORE_MISSES.WALK_COMPLETED / INST_RETIRED.ANY`
Load_Miss_Real_Latency - Actual Average Latency for L1 data-cache miss demand load operations (in core cycles)
`L1D_PEND_MISS.PENDING / MEM_LOAD_COMPLETED.L1_MISS_ANY`

ILP - Instruction-Level-Parallelism (average number of uops executed when there is execution) per-core
`UOPS_EXECUTED.THREAD / UOPS_EXECUTED.CORE_CYCLES_GE_1` or `UOPS_EXECUTED.THREAD / ( UOPS_EXECUTED.CORE_CYCLES_GE_1 / 2 )` if SMT is enabled. 
MLP - Memory-Level-Parallelism (average number of L1 miss demand load when there is at least one such miss. Per-Logical Processor)
`L1D_PEND_MISS.PENDING / L1D_PEND_MISS.PENDING_CYCLES`


DRAM_BW_Use - Average external Memory Bandwidth Use for reads and writes [GB / sec]
`( 64 * ( UNC_M_CAS_COUNT.RD + UNC_M_CAS_COUNT.WR ) / 1'000'000'000 ) / Time`
64, because it's the size of the cache line
IpCall - Instructions per (near) call (lower number means higher occurrence rate)
`INST_RETIRED.ANY / BR_INST_RETIRED.NEAR_CALL`

IpBranch - Instructions per Branch
`INST_RETIRED.ANY / BR_INST_RETIRED.ALL_BRANCHES`
IpLoad - Instructions per Load
`INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_LOADS_PS`
IpStore - Instructions per Store
`INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_STORES_PS`
IpMispredict - Number of Instructions per non-speculative Branch Misprediction
`INST_RETIRED.ANY / BR_MISP_RETIRED.ALL_BRANCHES`
IpFLOP - Instructions per Floating Point (FP) Operation 
`See TMA_metrics.xlsx`
IpArith - Instructions per FP Arithmetic instruction
`See TMA_metrics.xlsx`
IpArith_Scalar_SP - Instructions per FP Arithmetic Scalar Single-Precision instruction 

`INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_SINGLE`
IpArith_Scalar_DP - Instructions per FP Arithmetic Scalar Double-Precision instruction 
`INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_DOUBLE`

IpArith_AVX128 - Instructions per FP Arithmetic AVX/SSE 128-bit instruction 
`INST_RETIRED.ANY / ( FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE + FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE )`

IpArith_AVX256 - Instructions per FP Arithmetic AVX* 256-bit instruction 
`INST_RETIRED.ANY / ( FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE + FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE )`

IpSWPF - Instructions per Software prefetch instruction (of any type)
`INST_RETIRED.ANY / SW_PREFETCH_ACCESS.T0:u0xF`