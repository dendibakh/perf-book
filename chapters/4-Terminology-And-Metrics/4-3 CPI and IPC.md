

## CPI and IPC {#sec:IPC}

Those are two fundamental metrics that stand for:

* Instructions Per Cycle (IPC) - how many instructions were retired per cycle on average.

  $$
  IPC = \frac{INST\_RETIRED.ANY}{CPU\_CLK\_UNHALTED.THREAD},
  $$

where `INST_RETIRED.ANY` counts the number of retired instructions, and `CPU_CLK_UNHALTED.THREAD` counts the number of core cycles while the thread is not in a halt state.

* Cycles Per Instruction (CPI) - how many cycles it took to retire one instruction on average.

$$
CPI = \frac{1}{IPC}
$$

Using one or another is a matter of preference. I prefer to use IPC as it is easier to compare. With IPC, we want as many instructions per cycle as possible, so the higher the IPC, the better. With `CPI`, it's the opposite: we want as few cycles per instruction as possible, so the lower the CPI the better. The comparison that uses "the higher the better" metric is simpler since you don't have to do the mental inversion every time. In the rest of the book, we will mostly use IPC, but again, there is nothing wrong with using CPI either.

The relationship between IPC and CPU clock frequency is very interesting. In the broad sense, `performance = work / time`, where we can express work as the number of instructions and time as seconds. The number of seconds a program was running can be calculated as `total cycles / frequency`: 

$$
Performance = \frac{instructions \times frequency}{cycles} = IPC \times frequency
$$

As we can see, performance is proportional to IPC and frequency. If we increase any of the two metrics, the performance of a program will grow.

From the perspective of benchmarking, IPC and frequency are two independent metrics. I've seen some engineers mistakenly mixing them up and thinking that if you increase the frequency, the IPC will also go up. But that's not true. If you clock a processor at 1 GHz instead of 5 GHz, for many applications you will still get the same IPC.[^1] It may sound very confusing, especially since IPC has everything to do with CPU clocks. However, frequency only tells us how fast a single clock cycle is, whereas IPC counts how much work is done every cycle. So, from the benchmarking perspective, IPC solely depends on the design of the processor regardless of the frequency. Out-of-order cores typically have a much higher IPC than in-order cores. When you increase the size of CPU caches or improve branch prediction, the IPC usually goes up.

Now, if you ask a hardware architect, they will certainly tell you there is a dependency between IPC and frequency. From the CPU design perspective, you can deliberately downclock the processor, which will make every cycle longer and make it possible to squeeze more work into each cycle. In the end, you will get a higher IPC but a lower frequency. Hardware vendors approach this performance equation in different ways. For example, Intel and AMD chips usually have very high frequencies, with the recent Intel 13900KS processor providing a 6 GHz turbo frequency out of the box with no overclocking required. On the other hand, Apple M1/M2 chips have lower frequency but compensate with a higher IPC. Lower frequency facilitates lower power consumption. Higher IPC, on the other hand, usually requires a more complicated design, more transistors and a larger die size. We will not go into all the design tradeoffs here, as they are topics for a different book.

IPC is useful for evaluating both hardware and software efficiency. Hardware engineers use this metric to compare CPU generations and CPUs from different vendors. Since IPC is the measure of the performance of a CPU microarchitecture, engineers and media use it to express gains over the previous generation. However, to make a fair comparison, you need to run both systems at the same frequency.

IPC is also a useful metric for evaluating software. It gives you an intuition for how quickly instructions in your application progress through the CPU pipeline. Later in this chapter, you will see several production applications with varying IPCs. Memory-intensive applications usually have a low IPC (0--1), while computationally intensive workloads tend to have a high IPC (4--6).

Linux `perf` users can measure the IPC for their workload by running:

```bash
$ perf stat -e cycles,instructions -- a.exe
  2369632  cycles                               
  1725916  instructions  #    0,73  insn per cycle
# or as simple as:
$ perf stat -- ./a.exe
```

[^1]: When you lower CPU frequency, memory speed becomes faster relative to the CPU. This may hide actual memory bottlenecks and artificially increase IPC.
