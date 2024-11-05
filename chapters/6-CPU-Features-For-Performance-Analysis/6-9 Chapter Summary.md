## Chapter Summary {.unlisted .unnumbered}

\markright{Summary}

* Utilizing hardware features for low-level tuning is recommended only once all high-level performance issues are fixed. Tuning poorly designed algorithms is a bad investment of time. Once all the major performance problems are eliminated, you can use CPU performance monitoring features to analyze and further tune your application. 
* Top-down Microarchitecture Analysis (TMA) methodology is a very powerful technique for identifying ineffective usage of CPU microarchitecture by the program. It is a robust and formal methodology that is easy to use even for inexperienced developers. TMA is an iterative process that consists of multiple steps, including characterizing the workload and locating the exact place in the source code where the bottleneck occurs. We advise that TMA should be one of the starting points for every low-level tuning effort.
* Branch Record mechanisms such as Intel's LBR, AMD's LBR, and ARM's BRBE continuously log the most recent branch outcomes in parallel with executing the program, causing a minimal slowdown. One of the primary usages of these facilities is to collect call stacks. Also, they help identify hot branches, and misprediction rates and enable precise timing of machine code.
* Modern processors often provide Hardware-Based Sampling features for advanced profiling. Such features lower the sampling overhead by storing multiple samples in a dedicated buffer without software interrupts. They also introduce "Precise Events" that enable pinpointing the exact instruction that caused a particular performance event. In addition, there are several other less important use cases. Example implementations of such Hardware-Based Sampling features include Intel's PEBS, AMD's IBS, and ARM's SPE.
* Intel Processor Traces (PT) is a CPU feature that records the program execution by encoding packets in a highly compressed binary format that can be used to reconstruct execution flow with a timestamp on every instruction. PT has extensive coverage and a relatively small overhead. Its main usages are postmortem analysis and finding the root cause(s) of performance glitches. The Intel PT feature is covered in Appendix C. Processors based on ARM architecture also have a tracing capability called Arm [CoreSight](https://developer.arm.com/ip-products/system-ip/coresight-debug-and-trace),[^2] but it is mostly used for debugging rather than for performance analysis.
* Performance profilers leverage hardware features presented in this chapter to enable many different types of analysis.

[^2]: Arm CoreSight - [https://developer.arm.com/ip-products/system-ip/coresight-debug-and-trace](https://developer.arm.com/ip-products/system-ip/coresight-debug-and-trace)

\sectionbreak
