L1MPKI - L1 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L1_MISS_PS / INST_RETIRED.ANY`
L2MPKI - L2 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L2_MISS_PS / INST_RETIRED.ANY`
L3MPKI - L3 cache true misses per kilo instruction for retired demand loads
`1000 * MEM_LOAD_RETIRED.L3_MISS_PS / INST_RETIRED.ANY`
Branch_Mispredict_Ratio - Ratio of all branches which mispredict
`BR_MISP_RETIRED.ALL_BRANCHES / BR_INST_RETIRED.ALL_BRANCHES`
Code_STLB_MPKI - STLB (2nd level TLB) code speculative misses per kilo instruction (misses of any page-size that complete the page walk)
`1000 * ITLB_MISSES.WALK_COMPLETED / INST_RETIRED.ANY`
Load_STLB_MPKI - STLB (2nd level TLB) data load speculative misses per kilo instruction (misses of any page-size that complete the page walk)
`1000 * DTLB_LOAD_MISSES.WALK_COMPLETED / INST_RETIRED.ANY`
Store_STLB_MPKI - STLB (2nd level TLB) data store speculative misses per kilo instruction (misses of any page-size that complete the page walk)
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
IpBranch - Instructions per Branch (lower number means higher occurrence rate)
`INST_RETIRED.ANY / BR_INST_RETIRED.ALL_BRANCHES`
IpLoad - Instructions per Load (lower number means higher occurrence rate)
`INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_LOADS_PS`
IpStore - Instructions per Store (lower number means higher occurrence rate)
`INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_STORES_PS`
IpMispredict - Number of Instructions per non-speculative Branch Misprediction (JEClear) (lower number means higher occurrence rate)
`INST_RETIRED.ANY / BR_MISP_RETIRED.ALL_BRANCHES`

IpFLOP - Instructions per Floating Point (FP) Operation (lower number means higher occurrence rate)
`INST_RETIRED.ANY / #FLOP_Count`

IpArith - Instructions per FP Arithmetic instruction (lower number means higher occurrence rate). May undercount due to FMA double counting. Approximated prior to BDW.
`INST_RETIRED.ANY / ( #FP_Arith_Scalar + #FP_Arith_Vector )`

IpArith_Scalar_SP - Instructions per FP Arithmetic Scalar Single-Precision instruction (lower number means higher occurrence rate). May undercount due to FMA double counting.
`INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_SINGLE`
IpArith_Scalar_DP - Instructions per FP Arithmetic Scalar Double-Precision instruction (lower number means higher occurrence rate). May undercount due to FMA double counting.
`INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_DOUBLE`
IpArith_AVX128 - Instructions per FP Arithmetic AVX/SSE 128-bit instruction (lower number means higher occurrence rate). May undercount due to FMA double counting.
`INST_RETIRED.ANY / ( FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE + FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE )`
IpArith_AVX256 - Instructions per FP Arithmetic AVX* 256-bit instruction (lower number means higher occurrence rate). May undercount due to FMA double counting.
`INST_RETIRED.ANY / ( FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE + FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE )`
IpSWPF - Instructions per Software prefetch instruction (of any type: NTA/T0/T1/T2/Prefetch) (lower number means higher occurrence rate)
`INST_RETIRED.ANY / SW_PREFETCH_ACCESS.T0:u0xF`