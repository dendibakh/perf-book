---
typora-root-url: ..\..\img
---

## CPU Utilization

CPU utilization is the percentage of time the CPU was busy during some time period. Technically, a CPU is considered utilized when it is not running the kernel `idle` thread.

$$
CPU~Utilization = \frac{CPU\_CLK\_UNHALTED.REF\_TSC}{TSC},
$$
where `CPU_CLK_UNHALTED.REF_TSC` PMC counts the number of reference cycles when the core is not in a halt state, `TSC` stands for timestamp counter (discussed in [@sec:timers]), which is always ticking.

If CPU utilization is low, it usually means the poor performance of the application since some portion of the time was wasted by the CPU. However, high CPU utilization is not always good either. It is a sign that the system is doing some work but does not exactly say what it is doing: the CPU might be highly utilized even though it is stalled waiting on memory accesses. In a multithreaded context, a thread can also spin while waiting for resources to proceed, so there is Effective CPU utilization that filters spinning time (see [@sec:secMT_metrics]).

Linux `perf` automatically calculates CPU utilization across all CPUs on the system:

```bash
$ perf stat -- a.exe
  0.634874  task-clock (msec) #    0.773 CPUs utilized   
```
