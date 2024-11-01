## Collecting Performance Monitoring Events {#sec:counting}

Performance Monitoring Counters (PMCs) are a very important instrument of low-level performance analysis. They can provide unique information about the execution of a program. PMCs are generally used in two modes: "Counting" or "Sampling". The counting mode is primarily used for calculating various performance metrics that we discussed in [@sec:PerfMetrics]. The sampling mode is used for finding hotspots, which we will discuss soon.

The idea behind counting is very simple: we want to count the total number of certain performance monitoring events while our program is running. PMCs are heavily used in the Top-down Microarchitecture Analysis (TMA) methodology, which we will closely look at in [@sec:TMA]. Figure @fig:Counting illustrates the process of counting performance events from the start to the end of a program.

![Counting performance events.](../../img/perf-analysis/CountingFlow.png){#fig:Counting width=80%}

The steps outlined in Figure @fig:Counting roughly represent what a typical analysis tool will do to count performance events. A similar process is implemented in the `perf stat` tool, which can be used to count various hardware events, like the number of instructions, cycles, cache misses, etc. Below is an example of the output from `perf stat`:

```bash
$ perf stat -- ./my_program.exe
 10580290629  cycles         #    3,677 GHz
  8067576938  instructions   #    0,76  insn per cycle
  3005772086  branches       # 1044,472 M/sec
   239298395  branch-misses  #    7,96% of all branches 
```

This data may become quite handy. First of all, it enables us to quickly spot some anomalies, such as a high branch misprediction rate or low IPC. In addition, it might come in handy when you've made a code change and you want to verify that the change has improved performance. Looking at relevant events might help you justify or reject the code change. The `perf stat` utility can be used as a lightweight benchmark wrapper. It may serve as a first step in performance investigation. Sometimes anomalies can be spotted right away, which can save you some analysis time.

A full list of available event names can be viewed with `perf list`:

```bash
$ perf list
  cycles            [Hardware event]
  ref-cycles        [Hardware event]
  instructions      [Hardware event]
  branches          [Hardware event]
  branch-misses     [Hardware event]
  ...
cache:
  mem_load_retired.l1_hit
  mem_load_retired.l1_miss
  ...
```

Modern CPUs have hundreds of observable performance events. It's very hard to remember all of them and their meanings. Understanding when to use a particular event is even harder. That is why generally, I don't recommend manually collecting a specific event unless you really know what you are doing. Instead, I recommend using tools like Intel VTune Profiler that automate this process.

Performance events are not available in every environment since accessing PMCs requires root access, which applications running in a virtualized environment typically do not have. For programs executing in a public cloud, running a PMU-based profiler directly in a guest container does not result in useful output if a virtual machine (VM) manager does not expose the PMU programming interfaces properly to a guest. Thus profilers based on CPU performance monitoring counters do not work well in a virtualized and cloud environment [@PMC_virtual], although the situation is improving. VMware® was one of the first VM managers to enable[^4] virtual Performance Monitoring Counters (vPMC). The AWS EC2 cloud has also enabled[^5] PMCs for dedicated hosts.

### Multiplexing and Scaling Events {#sec:secMultiplex}

There are situations when we want to count many different events at the same time. However, with one counter, it's possible to count only one event at a time. That's why PMUs contain multiple counters (in Intel's recent Golden Cove microarchitecture there are 12 programmable PMCs, 6 per hardware thread). Even then, the number of fixed and programmable counters is not always sufficient. Top-down Microarchitecture Analysis (TMA) methodology requires collecting up to 100 different performance events in a single execution of a program. Modern CPUs don't have that many counters, and here is when multiplexing comes into play.

If you need to collect more events than the number of available PMCs, the analysis tool uses time multiplexing to give each event a chance to access the monitoring hardware. Figure @fig:Multiplexing1 shows an example of multiplexing between 8 performance events with only 4 counters available.

<div id="fig:Multiplexing">
![](../../img/perf-analysis/Multiplexing1.png){#fig:Multiplexing1 width=70%}

![](../../img/perf-analysis/Multiplexing2.png){#fig:Multiplexing2 width=80%}

Multiplexing between 8 performance events with only 4 PMCs available.
</div>

With multiplexing, an event is not measured all the time, but rather only during a portion of time. At the end of the run, a profiling tool needs to scale the raw count based on the total time enabled:
$$
final~count = raw~count \times ( time~running / time~enabled )
$$
Let's take Figure @fig:Multiplexing2 as an example. Say, during profiling, we were able to measure an event from group 1 during three time intervals. Each measurement interval lasted 100ms (`time enabled`). The program running time was 500ms (`time running`). The total number of events for this counter was measured as 10,000 (`raw count`). So, the final count needs to be scaled as follows:
$$
final~count = 10,000 \times ( 500ms / ( 100ms \times 3) ) = 16,666
$$
This provides an estimate of what the count would have been had the event been measured during the entire run. It is very important to understand that this is still an estimate, not an actual count. Multiplexing and scaling can be used safely on steady workloads that execute the same code during long time intervals. However, if the program regularly jumps between different hotspots, i.e., has different phases, there will be blind spots that can introduce errors during scaling. To avoid scaling, you can reduce the number of events to no more than the number of physical PMCs available. However, you'll have to run the benchmark multiple times to measure all the events.

[^4]: VMware PMCs - [https://www.vladan.fr/what-are-vmware-virtual-cpu-performance-monitoring-counters-vpmcs/](https://www.vladan.fr/what-are-vmware-virtual-cpu-performance-monitoring-counters-vpmcs/)
[^5]: Amazon EC2 PMCs - [http://www.brendangregg.com/blog/2017-05-04/the-pmcs-of-ec2.html](http://www.brendangregg.com/blog/2017-05-04/the-pmcs-of-ec2.html)
