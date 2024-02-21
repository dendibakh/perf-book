### TMA on AMD Platforms {#sec:secTMA_AMD}

Starting from Zen4, AMD processors support Level-1 and Level-2 TMA analysis. According to AMD documentation, it is called "Pipeline Utilization" analysis but the idea remains the same. The L1 and L2 buckets are also very similar to Intel's. Since kernel 6.2, Linux users can utilize the `perf` tool to collect the pipeline utilization data.

Next, we will examine [Crypto++](https://github.com/weidai11/cryptopp)[^1] implementation of SHA-256 (Secure Hash Algorithm 256), the fundamental cryptographic algorithm in Bitcoin mining. Crypto++ is an open-source C++ class library of cryptographic algorithms and contains an implementation of many algorithms, not just SHA-256. However, for our example, we disabled benchmarking all other algorithms by commenting out the corresponding line in the `BenchmarkUnkeyedAlgorithms` function in `bench1.cpp`.

We ran the test on an AMD Ryzen 9 7950X machine with Ubuntu 22.04, Linux kernel 6.5.0-15-generic. We compiled Crypto++ version 8.9 using GCC 12.3 C++ compiler. We used the default `-O3` optimization option, but it doesn't impact performance much since the code is written with x86 intrinsics (see [@sec:secIntrinsics]) and utilizes the SHA x86 ISA extension. 

Below is the command we used to obtain L1 and L2 pipeline utilization metrics. The output was trimmed and some statistics were dropped to remove unnecessary distraction.

```bash
$ perf stat -M PipelineL1,PipelineL2 -- ./cryptest.exe b1 10
 0.0 %  bad_speculation_mispredicts        (20.08%) 
 0.0 %  bad_speculation_pipeline_restarts  (20.08%)
 0.0 %  bad_speculation                    (20.08%)
 6.1 %  frontend_bound                     (20.00%)
 6.1 %  frontend_bound_bandwidth           (20.00%)
 0.1 %  frontend_bound_latency             (20.00%)
65.9 %  backend_bound_cpu                  (20.00%)
 1.7 %  backend_bound_memory               (20.00%)
67.5 %  backend_bound                      (20.00%)
26.3 %  retiring                           (20.08%)
20.2 %  retiring_fastpath                  (19.99%)
 6.1 %  retiring_microcode                 (19.99%)
```

In the output, numbers in brackets indicate the percentage of runtime duration, when a metric was monitored. As we can see, all the metrics were monitored only 20% of the time due to multiplexing. In our case it is likely not a concern as SHA256 has consistent behavior, however it may not always be the case. To minimize the impact of multiplexing, you can collect a limited set of metrics in a single run, e.g., `perf stat -M frontend_bound,backend_bound`.

A description of pipeline utilization metrics shown above can be found in [@AMDUprofManual, Chapter 2.8 Pipeline Utilization]. By looking at the metrics, we can see that branch mispredictions are not happening in SHA256 (`bad_speculation` is 0%). Only 26.3% of the available dispatch slots were used (`retiring`), which means the rest 73.7% were wasted due to frontend and backend stalls.

Crypto instructions are not trivial, so internally they are broken into smaller pieces ($\mu$ops). Once a processor encounters such an instruction, it retrieves $\mu$ops for it from the microcode. Microoperations are fetched from the microcode sequencer with a lower bandwidth than from regular instruction decoders, making it a potential source of performance bottlenecks. Crypto++ SHA256 implementation heavily uses instruction such as `SHA256MSG2`, `SHA256RNDS2`, and others which consist of multiple $\mu$ops according to [uops.info](https://uops.info/table.html)[^2] website. The `retiring_microcode` metric indicates that 6.1% of dispatch slots were used by microcode operations. The same number of dispatch slots were unused due to bandwidth bottleneck in the frontend (`frontend_bound_bandwidth`). Together, the two metrics suggest that those 6.1% of dispatch slots were wasted because the microcode sequencer has not been providing $\mu$ops while the backend could have consumed them.

[TODO]: Why do we have 6.1% for both `frontend_bound_bandwidth` AND `retiring_microcode`? Is there a specific relationship between those metrics? Did I describe it correctly in the text?

The majority of cycles are stalled in the CPU backend (`backend_bound`), but only 1.7% of cycles are stalled waiting for memory accesses (`backend_bound_memory`). So, we know that the benchmark is mostly limited by the computing capabilities of the machine. As you will know from Part 2 of this book, it could be related to either data flow dependencies or execution throughput of certain cryptographic operations. They are less frequent than traditional `ADD`, `SUB`, `CMP`, and other instructions and thus can be often executed only on a single execution unit. A large number of such operations may saturate the execution throughput of this particular unit. Further analysis should involve a closer look at the source code and generated assembly, checking execution port utilization, finding data dependencies, etc.; we will stop at this point.

When it comes to Windows, at the time of writing, TMA methodology is only supported on server platforms (codename Genoa), and not on client systems (codename Raphael). TMA support was added in AMD uProf version 4.1, but only in the command line tool `AMDuProfPcm` tool which is part of AMD uProf installation. You can consult [@AMDUprofManual, Chapter 2.8 Pipeline Utilization] for more details on how to run the analysis. The graphical version of AMD uProf doesn't have the TMA analysis yet. 

[^1]: Crypto++ - [https://github.com/weidai11/cryptopp](https://github.com/weidai11/cryptopp)
[^2]: uops.info - [https://uops.info/table.html](https://uops.info/table.html)