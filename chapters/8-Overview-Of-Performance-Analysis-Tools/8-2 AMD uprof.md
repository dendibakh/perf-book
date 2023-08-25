## AMD uProf

The [uProf](https://www.amd.com/en/developer/uprof.html) profiler is a tool developed by AMD for monitoring performance of applications running on AMD processors. While uProf can be used on Intel processors as well, you will be able to use only CPU-independent features. The profiler is available for free to download and can be used on Windows, Linux and FreeBSD. AMD uProf can be used for profiling on multiple virtual machines (VMs), including Microsoft Hyper-V, KVM, VMware ESXi, Citrix Xen, but not all features are available on all VMs. Also, uProf supports analyzing applications written in various languages, including C, C++, Java, .NET/CLR.

### How to configure it {.unlisted .unnumbered}

On Linux, uProf uses Linux perf for data collection. On Windows, uProf uses its own sampling driver that gets installed when you install uProf, no additional configuration is required. AMD uProf supports both command-line interface (CLI) and graphical interface (GUI). The CLI interface requires two separte steps - collect and report, similar to Linux perf.

### What you can do with it: {.unlisted .unnumbered}

- find hotspots: functions, statements, instructions.
- monitor various HW performance events and locate lines of code where these events happen.
- filter data for a specific function or thread.
- observe the workload behavior over time: view various performance events in timeline chart.
- analyze hot callpaths: call-graph, flame-graph and bottom-up charts.

Besides that uProf can monitor various OS events on Linux - thread state, thread synchronization, system calls, page faults, and others. It also allows to analyze OpenMP applications to detect thread imbalance, and analyze of MPI applications to detect the load imbalance among the nodes of MPI cluster. More details on various features of uProf can be found in the [User Guide](https://www.amd.com/en/developer/uprof.html#documentation)[^1].

### What you cannot do with it: {.unlisted .unnumbered}

Due to the sampling nature of the tool, it will eventually miss events with a very short duration. The reported samples are statistically estimated numbers, which are most of the time sufficient to analyze the performance but not the exact count of the events.

### Examples {.unlisted .unnumbered}

To demonstrate the look-and-feel of AMD uProf tool, we ran the dense LU matrix factorization component from the [Scimark2](https://math.nist.gov/scimark2/index.html)[^2] benchmark on AMD Ryzen 9 7950X, Windows 11, 64 GB RAM.

Figure @fig:uProfHotspots shows the function hotpots analysis. At the top of the image, you can see event timeline which shows the number of events observed at various times of the application execution. On the right, you can select which metric to plot, we selected `RETIRED_BR_INST_MISP`. Notice a spike in branch mispredictions in the time range from 20s to 40s. You can select this region to analyze closely what's going on there. Once you do that, it will update the bottom panels to show statistics only for that time interval.

![uProf's Function Hotspots view.](../../img/perf-tools/uProf_Hopspot.png){#fig:uProfHotspots width=100% }

Below the timeline graph, you can see a list of hot functions, along with corresponding sampled performance events and calculated metrics. Event counts can be viewed as: sample count, raw event count, and percentage. There are many interesting numbers to look at, however, we will not dive deep into the analysis, but readers are encouraged to figure out performance impact of branch mispredictions and find their source.

Below the functions table, you can see bottom-up callstack view for the selected funtion in the functions table. As we can see, the selected `LU_factor` function is called from `kernel_measureLU`, which in turn is called from `main`. In Scimark2 benchmark, this is the only call stack for `LU_factor`, even though is shows `Call Stacks [5]`, this is an artifact of collection that can be ignored. But in other applications, hot function can be called from many different places, so you would want to examine other call stacks as well. 

If you double-click on any function, uProf will open the source/assembly view for that function. We don't show this view for brevity. On the left panel, there are other views available, like Metrics, Flame Graph, Call Graph view, and Thread Concurrency. They are useful for analysis as well, however we decided to skip them. Readers can experiment and look at those views on their own.

[^1]: AMD uProf User Guide - [https://www.amd.com/en/developer/uprof.html#documentation](https://www.amd.com/en/developer/uprof.html#documentation)
[^2]: Scimark2 - [https://math.nist.gov/scimark2/index.html](https://math.nist.gov/scimark2/index.html)