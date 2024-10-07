### TMA on Intel Platforms {#sec:secTMA_Intel}

The TMA methodology was first proposed by Intel in 2014 and is supported starting from the Sandy Bridge family of processors. Intel's implementation supports nested categories for each high-level bucket that give a better understanding of the CPU performance bottlenecks in the program (see Figure @fig:TMA).

The workflow is designed to "drill down" to lower levels of the TMA hierarchy until we get to the very specific classification of a performance bottleneck. For example, at first, we collect metrics for the main four buckets: `Front End Bound`, `Back End Bound`, `Retiring`, and `Bad Speculation`. Say, we found out that a big portion of the program execution was stalled by memory accesses (which is a `Back End Bound` bucket, see Figure @fig:TMA). The next step is to run the workload again and collect metrics specific to the `Memory Bound` bucket only. The process is repeated until we know the exact root cause, for example, `L3 Bound`.

![The TMA hierarchy of performance bottlenecks. *© Image by Ahmad Yasin.*](../../img/pmu-features/TMAM.png){#fig:TMA width=90%}

It is fine to run the workload several times, each time drilling down and focusing on specific metrics. But usually, it is sufficient to run the workload once and collect all the metrics required for all levels of TMA. Profiling tools achieve that by multiplexing between different performance events during a single run (see [@sec:secMultiplex]). Also, in a real-world application, performance could be limited by several factors. For example, it can experience a large number of branch mispredictions (`Bad Speculation`) and cache misses (`Back End Bound`) at the same time. In this case, TMA will drill down into multiple buckets simultaneously and will identify the impact that each type of bottleneck makes on the performance of a program. Analysis tools such as Intel's VTune Profiler, AMD's uProf, and Linux `perf` can calculate all the TMA metrics with a single benchmark run. However, this only is acceptable if the workload is steady. Otherwise, you would better fall back to the original strategy of multiple runs and drilling down with each run.

The top two levels of TMA metrics are expressed in the percentage of all pipeline slots (see [@sec:PipelineSlot]) that were available during the execution of the program. It allows TMA to give an accurate representation of CPU microarchitecture utilization, taking into account the full bandwidth of the processor. Up to this point, everything should sum up nicely to 100%. However, starting from Level 3, buckets may be expressed in a different count domain, e.g., clocks and stalls. So they are not necessarily directly comparable with other TMA buckets.

The first step of TMA is to identify the performance bottleneck in the program. After we have done that, we need to know where exactly in the code it is happening. The second step in TMA is to locate the source of the problem down to the exact line of code and assembly instruction. The analysis methodology provides the exact performance event that you should use for each category of the performance problem. Then you can sample on this event to find the line in the source code that contributes to the performance bottleneck identified by the first stage. Don't worry if this process sounds complicated to you; everything becomes clear once you read through the case study.

### Case Study: Reduce The Number of Cache Misses with TMA {.unlisted .unnumbered}

As an example for this case study, we took a very simple benchmark, such that it is easy to understand and change. It is not representative of real-world applications, but it is good enough to demonstrate the workflow of TMA. We have a lot more practical examples in the second part of the book.

Most readers of this book will likely apply TMA to their own applications, with which they are familiar. But TMA is very effective even if you see the application for the first time. For this reason, we don't start by showing you the source code of the benchmark. But here is a short description: the benchmark allocates a 200 MB array on the heap, then enters a loop of 100M iterations. On every iteration of the loop, it generates a random index into the allocated array, performs some dummy work, and then reads the value from that index.

We ran the experiments on the machine equipped with an Intel Core i5-8259U CPU (Skylake-based) and 16GB of DRAM (DDR4 2400 MT/s), running 64-bit Ubuntu 20.04 (kernel version 5.13.0-27).

### Step 1: Identify the Bottleneck {.unlisted .unnumbered}

As a first step, we run our microbenchmark and collect a limited set of events that will help us calculate Level 1 metrics. Here, we try to identify high-level performance bottlenecks of our application by attributing them to the four L1 buckets: `Front End Bound`, `Back End Bound`, `Retiring`, and `Bad Speculation`. It is possible to collect Level 1 metrics using the Linux `perf` tool. The `perf stat` command has a dedicated `--topdown` option, however, in the recent version it will output these metrics by default. Below is the breakdown for our benchmark. The output of all commands in this section is trimmed to save space.

```bash
$ perf stat -- ./benchmark.exe
...
  TopdownL1 (cpu_core)  #  53.4 %  tma_backend_bound    <==
                        #   0.2 %  tma_bad_speculation
                        #  13.8 %  tma_frontend_bound
                        #  32.5 %  tma_retiring
...
```

By looking at the output, we can tell that the performance of the application is bound by the CPU backend. Let's drill one level down. Linux `perf` currently only supports Level 1 TMA metrics, so to get access to TMA metrics Level 2, 3, and further, we will use the `toplev` tool that is a part of [pmu-tools](https://github.com/andikleen/pmu-tools)[^7] written by Andi Kleen. It is implemented in `Python` and uses Linux `perf` under the hood. Specific Linux kernel settings must be enabled to use `toplev`; check the documentation for more details.

```bash
$ ~/pmu-tools/toplev.py --core S0-C0 -l2 -v --no-desc taskset -c 0 ./benchmark.exe
...
# Level 1
S0-C0  Frontend_Bound:                13.92 % Slots
S0-C0  Bad_Speculation:                0.23 % Slots
S0-C0  Backend_Bound:                 53.39 % Slots
S0-C0  Retiring:                      32.49 % Slots
# Level 2
S0-C0  Frontend_Bound.FE_Latency:     12.11 % Slots
S0-C0  Frontend_Bound.FE_Bandwidth:    1.84 % Slots
S0-C0  Bad_Speculation.Branch_Mispred: 0.22 % Slots
S0-C0  Bad_Speculation.Machine_Clears: 0.01 % Slots
S0-C0  Backend_Bound.Memory_Bound:    44.59 % Slots <==
S0-C0  Backend_Bound.Core_Bound:       8.80 % Slots
S0-C0  Retiring.Base:                 24.83 % Slots
S0-C0  Retiring.Microcode_Sequencer:   7.65 % Slots
```

In this command, we also pinned the process to CPU0 (using `taskset -c 0`) and limited the output of `toplev` to this core only (`--core S0-C0`). The option `-l2` tells the tool to collect Level 2 metrics. The option `--no-desc` disables the description of each metric.

We can see that the application’s performance is bound by memory accesses (`Backend_Bound.Memory_Bound`). Almost half of the CPU execution resources were wasted waiting for memory requests to complete. Now let us dig one level deeper: [^17]

```bash
$ ~/pmu-tools/toplev.py --core S0-C0 -l3 -v --no-desc taskset -c 0 ./benchmark.exe
...
# Level 1
S0-C0    Frontend_Bound:                 13.91 % Slots
S0-C0    Bad_Speculation:                 0.24 % Slots
S0-C0    Backend_Bound:                  53.36 % Slots
S0-C0    Retiring:                       32.41 % Slots
# Level 2
S0-C0    FE_Bound.FE_Latency:            12.10 % Slots
S0-C0    FE_Bound.FE_Bandwidth:           1.85 % Slots
S0-C0    BE_Bound.Memory_Bound:          44.58 % Slots
S0-C0    BE_Bound.Core_Bound:             8.78 % Slots
# Level 3
S0-C0-T0 BE_Bound.Mem_Bound.L1_Bound:     4.39 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.L2_Bound:     2.42 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.L3_Bound:     5.75 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.DRAM_Bound:  47.11 % Stalls <==
S0-C0-T0 BE_Bound.Mem_Bound.Store_Bound:  0.69 % Stalls
S0-C0-T0 BE_Bound.Core_Bound.Divider:     8.56 % Clocks
S0-C0-T0 BE_Bound.Core_Bound.Ports_Util: 11.31 % Clocks
```

We found the bottleneck to be in `DRAM_Bound`. This tells us that many memory accesses miss in all levels of caches and go all the way down to the main memory. We can also confirm this if we collect the absolute number of L3 cache misses for the program. For the Skylake architecture, the `DRAM_Bound` metric is calculated using the `CYCLE_ACTIVITY.STALLS_L3_MISS` performance event. Let’s collect it manually:

```bash
$ perf stat -e cycles,cycle_activity.stalls_l3_miss -- ./benchmark.exe
  32226253316  cycles
  19764641315  cycle_activity.stalls_l3_miss
```

The `CYCLE_ACTIVITY.STALLS_L3_MISS` event counts cycles when execution stalls, while the L3 cache miss demand load is outstanding. We can see that there are ~60% of such cycles, which is pretty bad.

### Step 2: Locate the Place in the Code {.unlisted .unnumbered}

As the second step in the TMA process, we locate the place in the code where the identified performance event occurs most frequently. To do so, one should sample the workload using an event that corresponds to the type of bottleneck that was identified during Step 1.

A recommended way to find such an event is to run `toplev` tool with the `--show-sample` option that will suggest the `perf record` command line that can be used to locate the issue. To understand the mechanics of TMA, we also present the manual way to find an event associated with a particular performance bottleneck. Correspondence between performance bottlenecks and performance events that should be used for determining the location of bottlenecks in source code can be done with the help of the [TMA metrics](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx)[^2] table. The `Locate-with` column denotes a performance event that should be used to locate the exact place in the code where the issue occurs. In our case, to find memory accesses that contribute to such a high value of the `DRAM_Bound` metric (miss in the L3 cache), we should sample on `MEM_LOAD_RETIRED.L3_MISS_PS` precise event. Here is the example command:

```bash
$ perf record -e cpu/event=0xd1,umask=0x20,name=MEM_LOAD_RETIRED.L3_MISS/ppp -- ./benchmark.exe
$ perf report -n --stdio
...
# Samples: 33K of event ‘MEM_LOAD_RETIRED.L3_MISS’
# Event count (approx.): 71363893
# Overhead   Samples  Shared Object   Symbol
# ........  ......... ..............  .................
#
    99.95%    33811   benchmark.exe   [.] foo
     0.03%       52   [kernel]        [k] get_page_from_freelist
     0.01%        3   [kernel]        [k] free_pages_prepare
     0.00%        1   [kernel]        [k] free_pcppages_bulk
```

Almost all L3 misses are caused by memory accesses in function `foo` inside executable `benchmark.exe`. Now it's time to look at the source code of the benchmark, which can be found on [GitHub](https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM).[^8]

To avoid compiler optimizations, function `foo` is implemented in assembly language, which is presented in [@lst:TMA_asm]. The “driver” portion of the benchmark is implemented in the `main` function, as shown in [@lst:TMA_cpp]. We allocate a big enough array `a` to make it not fit in the 6MB L3 cache. The benchmark generates a random index into array `a` and passes this index to the `foo` function along with the address of array `a`. Later the `foo` function reads this random memory location.[^11]

Listing: Assembly code of function foo.

~~~~ {#lst:TMA_asm .bash}
$ perf annotate --stdio -M intel foo
Percent |  Disassembly of benchmark.exe for MEM_LOAD_RETIRED.L3_MISS
------------------------------------------------------------
        :  Disassembly of section .text:
        :
        :  0000000000400a00 <foo>:
        :  foo():
   0.00 :    400a00:  nop  DWORD PTR [rax+rax*1+0x0]
   0.00 :    400a08:  nop  DWORD PTR [rax+rax*1+0x0]
                 ...  # more NOPs
 100.00 :    400e07:  mov  rax,QWORD PTR [rdi+rsi*1] <==
                 ...
   0.00 :    400e13:  xor  rax,rax
   0.00 :    400e16:  ret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Source code of function main.

~~~~ {#lst:TMA_cpp .cpp}
extern "C" { void foo(char* a, int n); }
const int _200MB = 1024*1024*200;
int main() {
  char* a = new char[_200MB]; // 200 MB buffer
  ...
  for (int i = 0; i < 100000000; i++) {
    int random_int = distribution(generator);
    foo(a, random_int);
  }
  ...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By looking at [@lst:TMA_asm], we can see that all L3 cache misses in function `foo` are tagged to a single instruction. Now that we know which instruction caused so many L3 misses, let’s fix it.

### Step 3: Fix the Issue {.unlisted .unnumbered}

There is dummy work emulated with NOPs at the beginning of the `foo` function. This creates a time window between the moment when we get the next address that will be accessed and the actual load instruction. The presence of the time windows allows us to start prefetching the memory location in parallel with the dummy work. [@lst:TMA_prefetch] shows this idea in action. More information about the explicit memory prefetching technique can be found in [@sec:memPrefetch].

Listing: Inserting memory prefetch into main.

~~~~ {#lst:TMA_prefetch .cpp}
  for (int i = 0; i < 100000000; i++) {
    int random_int = distribution(generator);
+   __builtin_prefetch ( a + random_int, 0, 1);
    foo(a, random_int);
  }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This explicit memory prefetching hint decreases execution time from 8.5 seconds to 6.5 seconds. Also, the number of `CYCLE_ACTIVITY.STALLS_L3_MISS` events becomes almost ten times less: it goes from 19 billion down to 2 billion.

TMA is an iterative process, so once we fix one problem, we need to repeat the process starting from Step 1. Likely it will move the bottleneck into another bucket, in this case, `Retiring`. This was an easy example demonstrating the workflow of TMA methodology. Analyzing real-world applications is unlikely to be that easy. Chapters in the second part of the book are organized to make them convenient for use with the TMA process. In particular, Chapter 8 covers the `Memory Bound` category, Chapter 9 covers `Core Bound`, Chapter 10 covers `Bad Speculation`, and Chapter 11 covers `FrontEnd Bound`. Such a structure is intended to form a checklist that you can use to drive code changes when you encounter a certain performance bottleneck.

#### Additional resources and links {.unlisted .unnumbered}

- Ahmad Yasin’s paper “A top-down method for performance analysis and counters architecture” [@TMA_ISPASS].
- Presentation "Software Optimizations Become Simple with Top-down Analysis on Intel Skylake" by Ahmad Yasin at IDF'15, URL: [https://youtu.be/kjufVhyuV_A](https://youtu.be/kjufVhyuV_A).
- Andi Kleen's blog: pmu-tools, part II: toplev, URL: [http://halobates.de/blog/p/262](http://halobates.de/blog/p/262).
- Toplev manual, URL: [https://github.com/andikleen/pmu-tools/wiki/toplev-manual](https://github.com/andikleen/pmu-tools/wiki/toplev-manual).

[^2]: TMA metrics - [https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx).
[^7]: PMU tools - [https://github.com/andikleen/pmu-tools](https://github.com/andikleen/pmu-tools).
[^8]: Case study example - [https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM](https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM).
[^11]: According to x86 calling conventions ([https://en.wikipedia.org/wiki/X86_calling_conventions](https://en.wikipedia.org/wiki/X86_calling_conventions)), the first 2 arguments land in `rdi` and `rsi` registers respectively.
[^17]: Alternatively, we could use the `-l2 --nodes L1_Bound,L2_Bound,L3_Bound,DRAM_Bound,Store_Bound` option instead of `-l3` to limit the collection since we know the application is bound by memory.
