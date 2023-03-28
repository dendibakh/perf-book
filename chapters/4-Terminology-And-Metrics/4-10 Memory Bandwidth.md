## Memory bandwidth and latency

TODO:

- Describe the difference between memory bandwidth and latency
- Tell that latency may increase under load.
- Give examples
- Describe Intel mlc (works on Intel and AMD), give alternatives for ARM
- Give output of mlc and comment it

```bash
Measuring Peak Injection Memory Bandwidths for the system
Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
Using all the threads from each core if Hyper-threading is enabled
Using traffic with the following read-write ratios
ALL Reads        :      34557.4
3:1 Reads-Writes :      30623.5
2:1 Reads-Writes :      29705.9
1:1 Reads-Writes :      29376.2
Stream-triad like:      31875.7
```

![L1/L2/L3 cache read latencies on Intel Core i7-1260P, measured with the mlc tool, large pages enabled.](../../img/terms-and-metrics/MemLatencies.png){#fig:MemoryLatenciesCharts width=100% }

Memory latency: P-core (89.7 ns), E-core (44.9 ns)

Using similar technique we can measure bandwidth of various components of the memory hierarchy.

![Block diagram of the memory hierarchy of Intel Core i7-1260P and external DDR4 memory.](../../img/terms-and-metrics/MemBandwidthAndLatenciesDiagram.png){#fig:MemBandwidthAndLatenciesDiagram width=100% }


- Notice, that we measure bandwidth in GB/s, thus it also depends on the frequency at which cores are running. That's why in reality, those numbers may be significantly lower. For example, L1 bw for P-core is X, when running solely on the system at full Turbo frequency. But the L1 bw for P-core may drop to 0.75X, when the system is fully loaded.
- Compare the output with maximums from Intel Advisor