## Intel Vtune

### General Information {.unlisted .unnumbered}

VTune Profiler (formerly VTune Amplifier) is a performance analysis tool for x86-based machines with a rich GUI interface. It can be run on Linux or Windows operating systems. We skip discussion about MacOS support for VTune since it doesn't work on Apple's chips (e.g. M1 and M2), and Intel-based Macbooks quickly become obsolete.

Vtune can be used on both Intel and AMD systems, many features will work. However, advanced hardware-based sampling requires an Intel-manufactured CPU. For example, you won't be able to collect HW performance counters on an AMD system with Intel Vtune.

As of early 2023, VTune is available for free as a stand-alone tool or as part of the Intel oneAPI Base Toolkit.

### How to configure it {.unlisted .unnumbered}

On Linux, Vtune can use two data collectors: Linux perf and Vtune's own driver called SEP. First type is used for user-mode sampling, but if you want to perform advanced analysis, you need to build and install SEP driver, which is not too hard.

```bash
# go to the sepdk folder in vtune's installation
$ cd ~/intel/oneapi/vtune/latest/sepdk/
# build the drivers
$ ./build-driver
# add vtune group and add your user to that group
# usually reboot is required after that
$ sudo groupadd vtune
$ sudo usermod -a -G vtune `whoami`
# install sep driver
$ sudo ./insmod-sep -r -g vtune
```

After you've done with the steps above, you should be able to use adanced analysis types like Microarchitectural Exploration and Memory Access.

Windows does not require any additional configuration after you install Vtune. Collecting hardware performance events requires administrator priveleges.

### What you can do with it: {.unlisted .unnumbered}

- find hotspots: functions, loops, statements.
- monitor various performance events, e.g. branch mispredictions and L3 cache misses.
- locate lines of code where these events happen.
- filter data for a specific function, time period or processor.
- observe the workload bahavior over time (incuding CPU frequency, memory bandwidth utilization, etc).

VTune can provide a very rich information about a running process. It is the right tool for you if you're looking to improve the overall performance of an application. Vtune always provides an aggregated data over some time period, so it can be used for finding optimization opportunities for the "average case". 

### What you cannot do with it: {.unlisted .unnumbered}

- analyze very short execution anomalies.
- observe system-wide complicated SW dynamics.

Due to the sampling nature of the tool, it will eventually miss events with a very short duration (e.g. submicrosecond).

### Examples {.unlisted .unnumbered}

Below is a series of screenshots of VTune's most interesting features. For the purpose of this example, we took POV-Ray, a ray tracer that is used to create 3D graphics. Figure @fig:VtuneHotspots shows the hotpots analysis of povray 3.7 built-in benchmark, compiled with clang14 compiler with `-O3 -ffast-math -march=native -g` options, and run on Intel Alderlake system (Core i7-1260P, 4 P-cores + 8 E-cores) with 4 worker threads. 

At the left part of the image, you can see a list of hot functions in the workload along with corresponding CPU time percentage and the number of retired instructions. On the right panel, you can see one of the most frequent call stacks that lead to calling the function `pov::Noise`. According to that screenshot, `44.4%` of the time function `pov::Noise`, was called from `pov::Evaluate_TPat`, which in turn was called from `pov::Compute_Pigment`. Notice that the call stack doesn't lead all the way to the `main` function. It happens because with HW-based collection, VTune uses LBR to sample call stacks, which has limited depth. Most likely we're dealing with recursive functions here, and to investigate that further users have to dig into the code.

![VTune's hotspots view of povray built-in benchmark.](../../img/perf-tools/VtunePovray.png){#fig:VtuneHotspots width=100% }

If you double-click on `pov::Noise` function, you will see an image that is shown on the figure @fig:VtuneSourceView. For the interest of space, only the most important columns are shown. Left panel shows the source code and CPU time that corresponds to each line of code. On the right, you can see a assembly instructions along with CPU time that was attributed to them. Highlighted machine instructions correspond to line 476 in the left panel. The sum of all CPU time percentages in both panels equals to the total CPU time attributed to the `pov::Noise`, which is `26.8%`.

![VTune's source code view of povray built-in benchmark.](../../img/perf-tools/VtunePovray_SourceView.png){#fig:VtuneSourceView width=100% }

I STOPPED HERE

Intel VTune can collect many different CPU performance events. To illustrate this, we ran a different analysis type, Microarchitecture Exploration. We already showed 

Another interesting
If you tick the mark

phases

At the bottom we 

One of the most powerful features of VTune is the ability to filter and regroup data. Users can select a region on the timeline and filter collected data only for that time interval. This will allow users to focus on that region and analyze what happened during 



[TODO]: provide screenshots
 1) hotspots view (filtered and zoomed).
 2) source code view.
 3) event count view.
 4) timeline view - show CPU freq and mem-bandwidth.
 5) microarchitectural exploration. (refer to example in section 7-1)
 
[TODO]: Briefly describe the memory access and threading analysis types.

[TODO]: Show usage of marker APIs.