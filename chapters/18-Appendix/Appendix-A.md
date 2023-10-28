---
typora-root-url: ..\..\img
---

# Appendix A. Reducing Measurement Noise {.unnumbered}

\markright{Appendix A}

Below are some examples of features that can contribute to increased non-determinism in performance measurements. See complete discussion in [@sec:secFairExperiments].

## Dynamic Frequency Scaling {.unnumbered .unlisted}

[Dynamic Frequency Scaling](https://en.wikipedia.org/wiki/Dynamic_frequency_scaling)[^11] (DFS) is a technique to increase the performance of the system by automatically raising CPU operating frequency when it runs demanding tasks. As an example of DFS implementation, Intel CPUs have a feature called [Turbo Boost](https://en.wikipedia.org/wiki/Intel_Turbo_Boost)[^1] and AMD CPUs employ [Turbo Core](https://en.wikipedia.org/wiki/AMD_Turbo_Core)[^2]functionality. 

Example of an impact Turbo Boost can make for a single-threaded workload running on Intel® Core™ i5-8259U:

```bash
# TurboBoost enabled
$ cat /sys/devices/system/cpu/intel_pstate/no_turbo
0
$ perf stat -e task-clock,cycles -- ./a.exe 
    11984.691958  task-clock (msec) #    1.000 CPUs utilized
  32,427,294,227  cycles            #    2.706 GHz
      11.989164338 seconds time elapsed

# TurboBoost disabled
$ echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
1
$ perf stat -e task-clock,cycles -- ./a.exe 
    13055.200832  task-clock (msec) #    0.993 CPUs utilized
  29,946,969,255  cycles            #    2.294 GHz
      13.142983989 seconds time elapsed
```

The average frequency is much higher when Turbo Boost is on.

DFS can be permanently disabled in BIOS[^3]. To programmatically disable the DFS feature on Linux systems, you need root access. Here is how one can achieve this:

```bash
# Intel
echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
# AMD
echo 0 > /sys/devices/system/cpu/cpufreq/boost
```
## Simultaneous Multithreading {.unnumbered .unlisted}

Modern CPU cores are often made in the simultaneous multithreading ([SMT](https://en.wikipedia.org/wiki/Simultaneous_multithreading)[^4]) manner. It means that in one physical core, you can have two threads of simultaneous execution. Typically, [architectural state](https://en.wikipedia.org/wiki/Architectural_state)[^5] is replicated, but the execution resources (ALUs, caches, etc.) are not. That means that if we have two separate processes running on the same core "simultaneously" (in different threads), they can steal resources from each other, for example, cache space.

SMT can be permanently disabled in BIOS[^6]. To programmatically disable SMT on Linux systems, you need root access. Here is how one can turn down a sibling thread in each core:

```bash
echo 0 > /sys/devices/system/cpu/cpuX/online
```
The sibling pairs of CPU threads can be found in the following files:

```bash
/sys/devices/system/cpu/cpuN/topology/thread_siblings_list
```

For example, on Intel® Core™ i5-8259U, which has 4 cores and 8 threads:

```bash
# all 8 HW threads enabled:
$ lscpu
...
CPU(s):              8
On-line CPU(s) list: 0-7
...
$ cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list
0,4
$ cat /sys/devices/system/cpu/cpu1/topology/thread_siblings_list
1,5
$ cat /sys/devices/system/cpu/cpu2/topology/thread_siblings_list
2,6
$ cat /sys/devices/system/cpu/cpu3/topology/thread_siblings_list
3,7

# Disabling SMT on core 0
$ echo 0 | sudo tee /sys/devices/system/cpu/cpu4/online
0
$ lscpu
CPU(s):               8
On-line CPU(s) list:  0-3,5-7
Off-line CPU(s) list: 4
...
$ cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list
0
```

## Scaling Governor {.unnumbered .unlisted}

Linux kernel is able to control CPU frequency for different purposes. One such purpose is to save the power, in which case the scaling governor[^7] inside the Linux Kernel can decide to decrease CPU operating frequency. For performance measurements, it is recommended to set the scaling governor policy to `performance` to avoid sub-nominal clocking. Here is how we can set it for all the cores:

```bash
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  echo performance > $i
done
```

## CPU Affinity {.unnumbered .unlisted}

[Processor affinity](https://en.wikipedia.org/wiki/Processor_affinity)[^8] enables the binding of a process to a certain CPU core(s). In Linux, one can do this with [`taskset`](https://linux.die.net/man/1/taskset)[^9] tool. Here 

```bash
# no affinity
$ perf stat -e context-switches,cpu-migrations -r 10 -- a.exe
               151      context-switches
                10      cpu-migrations

# process is bound to the CPU0
$ perf stat -e context-switches,cpu-migrations -r 10 -- taskset -c 0 a.exe 
               102      context-switches
                 0      cpu-migrations
```
notice the number of `cpu-migrations` gets down to `0`, i.e., the process never leaves the `core0`.

Alternatively, you can use [cset](https://github.com/lpechacek/cpuset)[^10] tool to reserve CPUs for just the program you are benchmarking. If using `Linux perf`, leave at least two cores so that `perf` runs on one core, and your program runs in another. The command below will move all threads out of N1 and N2 (`-k on` means that even kernel threads are moved out):

```bash
$ cset shield -c N1,N2 -k on
```

The command below will run the command after `--` in the isolated CPUs: 
```bash
$ cset shield --exec -- perf stat -r 10 <cmd>
```

## Process Priority {.unnumbered .unlisted}

In Linux, one can increase process priority using the `nice` tool. By increasing the priority process gets more CPU time, and the Linux scheduler favors it more in comparison with processes with normal priority. Niceness ranges from `-20` (highest priority value) to `19` (lowest priority value) with the default of `0`.

Notice in the previous example, execution of the benchmarked process was interrupted by the OS more than 100 times. If we increase process priority by run the benchmark with `sudo nice -n -N`:
```bash
$ perf stat -r 10 -- sudo nice -n -5 taskset -c 1 a.exe
    0   context-switches
    0   cpu-migrations
```
Notice the number of context-switches gets to `0`, so the process received all the computation time uninterrupted.

## Filesystem Cache {.unnumbered .unlisted}

Usually, an area of main memory is assigned to cache the file system contents, including various data. This reduces the need for an application to go all the way down to the disk. Here is an example of how file system cache can affect the running time of simple `git status` command:

```bash
# clean fs cache
$ echo 3 | sudo tee /proc/sys/vm/drop_caches && sync && time -p git status
real 2,57
# warmed fs cache
$ time -p git status
real 0,40
```

One can drop the current filesystem cache by running the following two commands:

```bash
$ echo 3 | sudo tee /proc/sys/vm/drop_caches
$ sync
```

Alternatively, you can make one dry run just to warm up the filesystem cache and exclude it from the measurements. This dry iteration can be combined with the validation of the benchmark output.

[^1]: Intel Turbo Boost - [https://en.wikipedia.org/wiki/Intel_Turbo_Boost](https://en.wikipedia.org/wiki/Intel_Turbo_Boost).
[^2]: AMD Turbo Core - [https://en.wikipedia.org/wiki/AMD_Turbo_Core](https://en.wikipedia.org/wiki/AMD_Turbo_Core).
[^3]: Intel Turbo Boost FAQ - [https://www.intel.com/content/www/us/en/support/articles/000007359/processors/intel-core-processors.html](https://www.intel.com/content/www/us/en/support/articles/000007359/processors/intel-core-processors.html).
[^4]: SMT - [https://en.wikipedia.org/wiki/Simultaneous_multithreading](https://en.wikipedia.org/wiki/Simultaneous_multithreading).
[^5]: Architectural state - [https://en.wikipedia.org/wiki/Architectural_state](https://en.wikipedia.org/wiki/Architectural_state).
[^6]: "How to disable hyperthreading" - [https://www.pcmag.com/article/314585/how-to-disable-hyperthreading](https://www.pcmag.com/article/314585/how-to-disable-hyperthreading).
[^7]: Documentation for Linux CPU frequency governors: [https://www.kernel.org/doc/Documentation/cpu-freq/governors.txt](https://www.kernel.org/doc/Documentation/cpu-freq/governors.txt).
[^8]: Processor affinity - [https://en.wikipedia.org/wiki/Processor_affinity](https://en.wikipedia.org/wiki/Processor_affinity).
[^9]: `taskset` manual - [https://linux.die.net/man/1/taskset](https://linux.die.net/man/1/taskset).
[^10]: `cpuset` manual - [https://github.com/lpechacek/cpuset](https://github.com/lpechacek/cpuset).
[^11]: Dynamic frequency scaling - [https://en.wikipedia.org/wiki/Dynamic_frequency_scaling](https://en.wikipedia.org/wiki/Dynamic_frequency_scaling).
