## Branch Recording Mechanisms {#sec:lbr}

Modern high-performance CPUs provide branch recording mechanisms that enable a processor to continuously log a set of previously executed branches. But before going into the details, you may ask: Why are we so interested in branches? Well, because this is how we can determine the control flow of a program. We largely ignore other instructions in a basic block (see [@sec:BasicBlock]) because a branch is always the last instruction in a basic block. Since all instructions in a basic block are guaranteed to be executed once, we can only focus on branches that will “represent” the entire basic block. Thus, it’s possible to reconstruct the entire line-by-line execution path of the program if we track the outcome of every branch. This is what the Intel Processor Traces (PT) feature is capable of doing, which is discussed in Appendix C. Branch recording mechanisms that we will discuss in this section are based on sampling, not tracing, and thus have different use cases and capabilities.

Processors designed by Intel, AMD, and Arm all have announced their branch recording extensions. Exact implementations may vary but the idea is the same: hardware logs the “from” and “to” addresses of each branch along with some additional data in parallel with executing the program. If we collect a long enough history of source-destination pairs, we will be able to unwind the control flow of our program, just like a call stack, but with limited depth. Such extensions are designed to cause minimal slowdown to a running program (often within 1%).

With a branch recording mechanism in place, we can sample on branches (or cycles, it doesn't matter), but during each sample, look at the previous N branches that were executed. This gives us reasonable coverage of the control flow in the hot code paths but does not overwhelm us with too much information, as only a small number of total branches are examined. It is important to keep in mind that this is still sampling, so not every executed branch can be examined. A CPU generally executes too fast for that to be feasible.

It is very important to keep in mind that only taken branches are being logged. [@lst:LogBranches] shows an example of how branch results are being tracked. This code represents a loop with three instructions that may change the execution path of the program, namely loop back edge `JNE` (1), conditional branch `JNS` (2), function `CALL` (3), and return address from this function (4).

Listing: Example of logging branches.

~~~~ {#lst:LogBranches .asm}
----> 4eda10:  mov   edi,DWORD PTR [rbx]
|     4eda12:  test  edi,edi
| --- 4eda14:  jns   4eda1e              <== (2)
| |   4eda16:  mov   eax,edi
| |   4eda18:  shl   eax,0x7
| |   4eda1b:  lea   edi,[rax+rdi*8]
| └─> 4eda1e:  call  4edb26              <== (3)
|     4eda23:  add   rbx,0x4             <== (4)
|     4eda27:  mov   DWORD PTR [rbx-0x4],eax
|     4eda2a:  cmp   rbx,rbp
----- 4eda2d:  jne   4eda10              <== (1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is one possible branch history that can be logged with a branch recording mechanism. It shows the last 7 branch outcomes (many more not shown) at the moment we executed the `CALL` instruction. Because on the latest iteration of the loop, the `JNS` branch (`4eda14` &rarr; `4eda1e`) was not taken, it is not logged and thus does not appear in the history.

```
    Source Address    Destination Address
    ...               ...
(1) 4eda2d            4eda10    <== next iteration              │
(2) 4eda14            4eda1e    <== jns taken                   │
(3) 4eda1e            4edb26    <== call a function             │ 
(4) 4b01cd            4eda23    <== return from a function      │ time
(1) 4eda2d            4eda10    <== next iteration              │ 
(3) 4eda1e            4edb26    <== latest branch               V 
```

The fact that untaken branches are not logged might add a burden for analysis but usually, it doesn’t complicate it too much. We can still infer the complete execution path since we know that the control flow was sequential from the destination address in the entry `N-1` to the source address in the entry `N`.

Next, we will take a look at each vendor's branch recording mechanism and then explore how they can be used in performance analysis.

### LBR on Intel Platforms

Intel first implemented its Last Branch Record (LBR) facility in the NetBurst microarchitecture. Initially, it could record only the 4 most recent branch outcomes. It was later enhanced to 16 starting with Nehalem and to 32 starting from Skylake. Prior to the Golden Cove microarchitecture, LBR was implemented as a set of model-specific registers (MSRs), but now it works within architectural registers.[^12]

The LBR registers act like a ring buffer that is continuously overwritten and provides only 32 most recent branch outcomes. Each LBR entry is comprised of three 64-bit values:

- The source address of the branch (`From IP`).
- The destination address of the branch (`To IP`).
- Metadata for the operation, including mispredict, and elapsed cycle time information.

There are important applications to the additional information saved besides just source and destination addresses, which we will discuss later.

When a sampling counter overflows and a Performance Monitoring Interrupt (PMI) is triggered, the LBR logging freezes until the software captures the LBR records and resumes collection.

LBR collection can be limited to a set of specific branch types, for example, a user may choose to log only function calls and returns. Applying such a filter to the code in [@lst:LogBranches], we would only see branches (3) and (4) in the history. Users can also filter in/out conditional and unconditional jumps, indirect jumps and calls, system calls, interrupts, etc. In Linux perf, there is a `-j` option that enables/disables the recording of various branch types.

By default, the LBR array works as a ring buffer that captures control flow transitions. However, the depth of the LBR array is limited, which can be a limiting factor when profiling applications in which a transition of the execution flow is accompanied by a large number of leaf function calls. These calls to leaf functions, and their returns, are likely to displace the main execution context from the LBRs. Consider the example in [@lst:LogBranches] again. Say we want to unwind the call stack from the history in LBR, and so we configured LBR to capture only function calls and returns. If the loop runs thousands of iterations, then taking into account that the LBR array is only 32 entries deep, there is a very high chance we would only see 16 pairs of entries (3) and (4). In such a scenario, the LBR array is cluttered with leaf function calls which don't help us to unwind the current call stack.

This is why LBR supports call-stack mode. With this mode enabled, the LBR array captures function calls as before, but as return instructions are executed the last captured branch (`call`) record is flushed from the array in a last-in-first-out (LIFO) manner. Thus, branch records with completed leaf functions will not be retained, while preserving the call stack information of the main line execution path. When configured in this manner, the LBR array emulates a call stack, where a `CALL` instruction pushes and a `RET` instruction pops entry from the stack. If the depth of the call stack in your application never goes beyond 32 nested frames, LBRs will give you very accurate information. [@IntelOptimizationManual, Volume 3B, Chapter 19 Last Branch Records]

You can make sure LBRs are enabled on your system with the following command:

```bash
$ dmesg | grep -i lbr
[    0.228149] Performance Events: PEBS fmt3+, 32-deep LBR, Skylake events, full-width counters, Intel PMU driver.
```

With Linux `perf`, you can collect LBR stacks using the following command:

```bash
$ perf record -b -e cycles -- ./benchmark.exe
[ perf record: Woken up 68 times to write data ]
[ perf record: Captured and wrote 17.205 MB perf.data (22089 samples) ]
```

LBR stacks can also be collected using the `perf record --call-graph lbr` command, but the amount of information collected is less than using `perf record -b`. For example, branch misprediction and cycles data are not collected when running `perf record --call-graph lbr`.

Because each collected sample captures the entire LBR stack (32 last branch records), the size of collected data (`perf.data`) is significantly bigger than sampling without LBRs. Still, the runtime overhead for the majority of LBR use cases is below 1%. [@Nowak2014TheOO]

Users can export raw LBR stacks for custom analysis. Below is the Linux perf command you can use to dump the contents of collected branch stacks:

```bash
$ perf record -b -e cycles -- ./benchmark.exe
$ perf script -F brstack &> dump.txt
```

The `dump.txt` file, which can be quite large, contains lines like those shown below:

```
...
0x4edaf9/0x4edab0/P/-/-/29
0x4edabd/0x4edad0/P/-/-/2
0x4edadd/0x4edb00/M/-/-/4
0x4edb24/0x4edab0/P/-/-/24
0x4edabd/0x4edad0/P/-/-/2
0x4edadd/0x4edb00/M/-/-/1
0x4edb24/0x4edab0/P/-/-/3
0x4edabd/0x4edad0/P/-/-/1
...
```

In the output above, we present eight entries from the LBR stack, which typically consists of 32 LBR entries. Each entry has `FROM` and `TO` addresses (hexadecimal values), a predicted flag (this one single branch outcome was `M` - Mispredicted, `P` - Predicted), and the number of cycles since the previous record (number in the last position of each entry). Components marked with "`-`" are related to transactional memory extension (TSX), which we won't discuss here. Curious readers can look up the format of a decoded LBR entry in the `perf script` [specification](http://man7.org/linux/man-pages/man1/perf-script.1.html)[^2].

### LBR on AMD Platforms

AMD processors also support Last Branch Record (LBR) on AMD Zen4 processors. Zen4 can log 16 pairs of "from" and "to" addresses along with some additional metadata. Similar to Intel LBR, AMD processors can record various types of branches. The main difference from Intel LBR is that AMD processors don't support call stack mode yet, hence the LBR feature can't be used for call stack collection. Another noticeable difference is that there is no cycle count field in the AMD LBR record. For more details see [@AMDProgrammingManual, 13.1.1.9 Last Branch Stack Registers].

Since Linux kernel 6.1 onwards, Linux `perf` on AMD Zen4 processors supports the branch analysis use cases we discuss below unless explicitly mentioned otherwise. The Linux `perf` commands use the same `-b` and `-j` options as on Intel processors.

Branch analysis is also possible with the AMD uProf CLI tool. The example command below dumps collected raw LBR records and generates a CSV report:

```bash
$ AMDuProfCLI collect --branch-filter -o /tmp/ ./AMDTClassicMatMul-bin
```

### BRBE on Arm Platforms

Arm introduced its branch recording extension called BRBE in 2020 as a part of the ARMv9.2-A ISA. Arm BRBE is very similar to Intel's LBR and provides many similar features. Just like Intel's LBR, BRBE records contain source and destination addresses, a misprediction bit, and a cycle count value. According to the latest available BRBE specification, the call stack mode is not supported. The Branch records only contain information for a branch that is architecturally executed, i.e., not on a mispredicted path. Users can also filter records based on specific branch types. One notable difference is that BRBE supports configurable depth of the BRBE buffer: processors can choose the capacity of the BRBE buffer to be 8, 16, 32, or 64 records. More details are available in [@Armv9ManualSupplement, Chapter F1 "Branch Record Buffer Extension"].

At the time of writing, there were no commercially available machines that implement ARMv9.2-A, so it is not possible to test the BRBE extension in action.

Several use cases become possible thanks to branch recording. Next, we will cover the most important ones.

### Capture Call Stacks

One of the most popular use cases for branch recording is capturing call stacks. I already covered why we need to collect them in [@sec:secCollectCallStacks]. Branch recording can be used as a lightweight substitution for collecting call graph information even if you compiled a program without frame pointers or debug information.

At the time of writing (late 2023), AMD's LBR and Arm's BRBE don't support call stack collection, but Intel's LBR does. Here is how you can do it with Intel LBR:

```bash
$ perf record --call-graph lbr -- ./a.exe
$ perf report -n --stdio
# Children   Self    Samples  Command  Object  Symbol
# ........  .......  .......  .......  ......  .......
	99.96%  99.94%    65447    a.exe    a.exe  [.] bar
            |
             --99.94%--main
                       |
                       |--90.86%--foo
                       |          |
                       |           --90.86%--bar
                       |
                        --9.08%--zoo
                                  bar
```

As you can see, we identified the hottest function in the program (which is `bar`). Also, we identified callers that contribute to the most time spent in function `bar`: 91% of the time the tool captured the `main` &rarr; `foo` &rarr; `bar` call stack, and 9% of the time it captured `main` &rarr; `zoo` &rarr; `bar`. In other words, 91% of samples in `bar` have `foo` as its caller function.

It's important to mention that we cannot necessarily drive conclusions about function call counts in this case. For example, we cannot say that `foo` calls `bar` 10 times more frequently than `zoo`. It could be the case that `foo` calls `bar` once, but it executes an expensive path inside `bar` while `zoo` calls `bar` many times but returns quickly from it.

### Identify Hot Branches {#sec:lbr_hot_branch}

Branch recording also enables us to identify the most frequently taken branches. It is supported on Intel and AMD. According to Arm's BRBE specification, it can be supported, but due to the unavailability of processors that implement this extension, it is not possible to verify. Here is an example:

```bash
$ perf record -e cycles -b -- ./a.exe
[ perf record: Woken up 3 times to write data ]
[ perf record: Captured and wrote 0.535 MB perf.data (670 samples) ]
$ perf report -n --sort overhead,srcline_from,srcline_to -F +dso,symbol_from,symbol_to --stdio
# Samples: 21K of event 'cycles'
# Event count (approx.): 21440
# Overhead  Samples  Object  Source Sym  Target Sym  From Line  To Line
# ........  .......  ......  ..........  ..........  .........  .......
  51.65%      11074   a.exe   [.] bar    [.] bar      a.c:4      a.c:5
  22.30%       4782   a.exe   [.] foo    [.] bar      a.c:10     (null)
  21.89%       4693   a.exe   [.] foo    [.] zoo      a.c:11     (null)
   4.03%        863   a.exe   [.] main   [.] foo      a.c:21     (null)
```

From this example, we can see that more than 50% of taken branches are within the `bar` function, 22% of branches are function calls from `foo` to `bar`, and so on. Notice how `perf` switched from `cycles` event to analyzing LBR stacks: only 670 samples were collected, yet we have an entire 32-entry LBR stack captured with every sample. This gives us `670 * 32 = 21440` LBR entries (branch outcomes) for analysis.[^5]

Most of the time, it’s possible to determine the location of the branch just from the line of code and target symbol. However, theoretically, you could write code with two `if` statements written on a single line. Also, when expanding the macro definition, all the expanded code is attributed to the same source line, which is another situation when this might happen. This issue does not completely block the analysis but only makes it a little more difficult. To disambiguate two branches, you likely need to analyze raw LBR stacks yourself (see example on [easyperf](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)[^6] blog).

Using branch recording, we can also find a *hyperblock* (sometimes called *superblock*), which is a chain of hot basic blocks in a function that are not necessarily laid out in the sequential physical order but are executed sequentially. Thus, a hyperblock represents a typical hot path inside a function.

### Analyze Branch Misprediction Rate {#sec:secLBR_misp_rate}

Thanks to the mispredict bit in the additional information saved inside each record, it is also possible to know the misprediction rate for hot branches. In this example, we take a C-code-only version of the 7-zip benchmark from the LLVM test suite.[^7] The output of the `perf report` command is slightly trimmed to fit nicely on a page. The following use case is supported on Intel and AMD. According to Arm's BRBE specification, it can be supported, but due to the unavailability of processors that implement this extension, it is not possible to verify.

```bash
$ perf record -e cycles -b -- ./7zip.exe b
$ perf report -n --sort symbol_from,symbol_to -F +mispredict,srcline_from,srcline_to --stdio
# Samples: 657K of event 'cycles'
# Event count (approx.): 657888
# Overhead  Samples  Mis  From Line  To Line  Source Sym  Target Sym
# ........  .......  ...  .........  .......  ..........  ..........
    46.12%   303391   N   dec.c:36   dec.c:40  LzmaDec     LzmaDec
    22.33%   146900   N   enc.c:25   enc.c:26  LzmaFind    LzmaFind
     6.70%    44074   N   lz.c:13    lz.c:27   LzmaEnc     LzmaEnc
     6.33%    41665   Y   dec.c:36   dec.c:40  LzmaDec     LzmaDec
```

In this example, the lines that correspond to function `LzmaDec` are of particular interest to us. In the output that Linux `perf` provides, we can spot two entries that correspond to the `LzmaDec` function: one with `Y` and one with `N` letters. We can conclude that the branch on source line `dec.c:36` is the most executed in the benchmark since more than 50% of samples are attributed to it. Analyzing those two entries together gives us a misprediction rate for the branch. We know that the branch on line `dec.c:36` was predicted `303391` times (corresponds to `N`) and was mispredicted `41665` times (corresponds to `Y`), which gives us an `88%` prediction rate.

Linux `perf` calculates the misprediction rate by analyzing each LBR entry and extracting a misprediction bit from it. So for every branch, we have a number of times it was predicted correctly and a number of mispredictions. Again, due to the nature of sampling, some branches might have an `N` entry but no corresponding `Y` entry. It means there are no LBR entries for the branch being mispredicted, but that doesn’t necessarily mean the prediction rate is `100%`.

### Precise Timing of Machine Code {#sec:timed_lbr}

As we showed in Intel's LBR section, starting from Skylake microarchitecture, there is a special `Cycle Count` field in the LBR entry. This additional field specifies the number of elapsed cycles between two taken branches. Since the target address in the previous (N-1) LBR entry is the beginning of a basic block (BB) and the source address of the current (N) LBR entry is the last instruction of the same basic block, then the cycle count is the latency of this basic block.

This type of analysis is not supported on AMD platforms since they don't record a cycle count in the LBR record. According to Arm's BRBE specification, it can be supported, but due to the unavailability of processors that implement this extension, it is not possible to verify. However, Intel supports it. Here is an example:

```
400618:   movb  $0x0, (%rbp,%rdx,1)    <= start of the BB
40061d:   add $0x1, %rdx
400621:   cmp $0xc800000, %rdx
400628:   jnz 0x400644                 <= end of the BB
```

Suppose we have the following entries in the LBR stack:

```
  FROM_IP   TO_IP    Cycle Count
  ...       ...      ...        <== 26 entries
  40060a    400618    10
  400628    400644    80        <== occurrence 1 
  40064e    400600     3
  40060a    400618     9
  400628    400644   300        <== occurrence 2
  40064e    400600     3        <== LBR TOS
```

Given that information, we have two occurrences of the basic block that starts at offset `400618`. The first one was completed in 80 cycles, while the second one took 300 cycles. If we collect enough samples like that, we could plot an occurrence rate chart of latency for that basic block.

An example of such a chart is shown in Figure @fig:LBR_timing_BB. It was compiled by analyzing relevant LBR entries. The way to read this chart is as follows: it tells what was the rate of occurrence of a given latency value. For example, the basic block latency was measured as 100 cycles roughly 2% of the time, 14% of the time we measured 280 cycles, and never saw anything between 150 and 200 cycles. Another way to read is: based on the collected data, what is the probability of seeing a certain basic block latency if you were to measure it?

![Occurrence rate chart for latency of the basic block that starts at address `0x400618`.](../../img/pmu-features/LBR_timing_BB.png){#fig:LBR_timing_BB width=90%}

We can see two humps: a small one around 80 cycles \circled{1} and two bigger ones at 280 and 305 cycles \circled{2}. The block has a random load from a large array that doesn’t fit in the CPU L3 cache, so the latency of the basic block largely depends on this load. Based on the chart we can conclude that the first spike \circled{1} corresponds to the L3 cache hit and the second spike \circled{2} corresponds to the L3 cache miss where the load request goes all the way down to the main memory.

This information can be used for a fine-grained tuning of this basic block. This example might benefit from memory prefetching, which we will discuss in [@sec:memPrefetch]. Also, cycle count information can be used for timing loop iterations, where every loop iteration ends with a taken branch (back edge).

Before the proper support from profiling tools was in place, building graphs similar to Figure @fig:LBR_timing_BB required manual parsing of raw LBR dumps. An example of how to do this can be found on the [easyperf blog](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf)[^9]. Luckily, in newer versions of Linux perf, obtaining this information is much easier. The example below demonstrates this method directly using Linux perf on the same 7-zip benchmark from the LLVM test suite we introduced earlier:

```bash
$ perf record -e cycles -b -- ./7zip.exe b
$ perf report -n --sort symbol_from,symbol_to -F +cycles,srcline_from,srcline_to --stdio
# Samples: 658K of event 'cycles'
# Event count (approx.): 658240
# Overhead  Samples  BBCycles  FromSrcLine  ToSrcLine
# ........  .......  ........  ...........  ..........
     2.82%   18581      1      dec.c:325    dec.c:326
     2.54%   16728      2      dec.c:174    dec.c:174
     2.40%   15815      4      dec.c:174    dec.c:174
     2.28%   15032      2      find.c:375   find.c:376
     1.59%   10484      1      dec.c:174    dec.c:174
     1.44%   9474       1      enc.c:1310   enc.c:1315
     1.43%   9392      10      7zCrc.c:15   7zCrc.c:17
     0.85%   5567      32      dec.c:174    dec.c:174
     0.78%   5126       1      enc.c:820    find.c:540
     0.77%   5066       1      enc.c:1335   enc.c:1325
     0.76%   5014       6      dec.c:299    dec.c:299
     0.72%   4770       6      dec.c:174    dec.c:174
     0.71%   4681       2      dec.c:396    dec.c:395
     0.69%   4563       3      dec.c:174    dec.c:174
     0.58%   3804      24      dec.c:174    dec.c:174
```

Notice we've added the `-F +cycles` option to show cycle counts in the output (`BBCycles` column). Several insignificant lines were removed from the output of the `perf report` to make it fit on the page. Let's focus on lines in which the source and destination are `dec.c:174`, there are seven such lines in the output. In the source code, the line `dec.c:174` expands a macro that has a self-contained branch. That’s why the source and destination point to the same line.

Linux `perf` sorts entries by overhead first, so we need to manually filter entries for the branch in which we are interested. Luckily, they can be grepped very easily. In fact, if we filter them, we will get the latency distribution for the basic block that ends with this branch, as shown in Table {@tbl:bb_latency}. This data can be plotted to obtain a chart similar to the one shown in Figure @fig:LBR_timing_BB.

----------------------------------------------
Cycles  Number of samples  Occurrence rate
------  -----------------  -------------------
1       10484              17.0%

2       16728              27.1%

3       4563                7.4%

4       15815              25.6%

6       4770                7.7%

24      3804                6.2%

32      5567                9.0%
----------------------------------------------

Table: Occurrence rate for basic block latency. {#tbl:bb_latency}

Here is how we can interpret the data: from all the collected samples, 17% of the time the latency of the basic block was one cycle, 27% of the time it was 2 cycles, and so on. Notice a distribution mostly concentrates from 1 to 6 cycles, but also there is a second mode of much higher latency of 24 and 32 cycles, which likely corresponds to branch misprediction penalty. The second mode in the distribution accounts for 15% of all samples.

This example shows that it is feasible to plot basic block latencies not only for tiny microbenchmarks but for real-world applications as well. Currently, LBR is the most precise cycle-accurate source of timing information on Intel systems.

### Estimating Branch Outcome Probability

Later in [@sec:secFEOpt], we will discuss the importance of code layout for performance. Going forward a little bit, having a hot path fall through[^11] generally improves the performance of a program. Knowing the most frequent outcome of a certain branch enables developers and compilers to make better optimization decisions. For example, given that a branch is taken 99% of the time, we can try to invert the condition and convert it to a non-taken branch.

LBR enables us to collect this data without instrumenting the code. As the outcome from the analysis, a user will get a ratio between true and false outcomes of the condition, i.e., how many times the branch was taken and how much was not taken. This feature especially shines when analyzing indirect jumps (switch statements) and indirect calls (virtual calls). You can find examples of using it on a real-world application on the [easyperf blog](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)[^6].

### Providing Compiler Feedback Data

We will discuss Profile Guided Optimizations (PGO) later in [@sec:secPGO], so just a quick mention here. Branch recording mechanisms can provide profiling feedback data for optimizing compilers. Imagine that we can feed all the data we discovered in the previous sections back to the compiler. In some cases, this data cannot be obtained using traditional static code instrumentation, so branch recording mechanisms are not only a better choice because of the lower overhead, but also because of richer profiling data. PGO workflows that rely on data collected from the hardware PMU are becoming more popular and likely will take off sharply once the support in AMD and Arm matures.

[^2]: Linux `perf script` manual page - [http://man7.org/linux/man-pages/man1/perf-script.1.html](http://man7.org/linux/man-pages/man1/perf-script.1.html).
[^5]: The report header generated by perf might still be confusing because it says `21K of event cycles`. But there are `21K` LBR entries, not `cycles`.
[^6]: Easyperf: Estimating Branch Probability - [https://easyperf.net/blog/2019/05/06/Estimating-branch-probability](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)
[^7]: LLVM test-suite 7zip benchmark - [https://github.com/llvm-mirror/test-suite/tree/master/MultiSource/Benchmarks/7zip](https://github.com/llvm-mirror/test-suite/tree/master/MultiSource/Benchmarks/7zip)
[^9]: Easyperf: Building a probability density chart for the latency of an arbitrary basic block - [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf).
[^11]: I.e., when the hot branches are not taken.
[^12]: Its primary advantage is that LBR features are clearly defined and there is no need to check the exact model number of the current CPU. It makes support in the OS and profiling tools much easier. Also, LBR entries can be configured to be included in the PEBS records (see [@sec:secPEBS]).
