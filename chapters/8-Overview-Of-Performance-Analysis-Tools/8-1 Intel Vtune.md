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

[TODO]: provide screenshots
 1) hotspots view (filtered and zoomed).
 2) source code view.
 3) event count view.
 4) timeline view - show CPU freq and mem-bandwidth.
 5) microarchitectural exploration. (refer to example in section 7-1)
 
[TODO]: Briefly describe the memory access and threading analysis types.

[TODO]: Show usage of marker APIs.