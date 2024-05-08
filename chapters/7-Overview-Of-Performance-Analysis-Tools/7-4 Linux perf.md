## Linux Perf

Linux Perf is probably the most used performance profiler in the world, due to the fact that it is available on most Linux distributions, which makes it accessible for a wide range of users. Perf is natively supported in many popular Linux distributions, including Ubuntu, Red Hat, Debian, and many others. It is included in the kernel, so you can get OS-level statistic (page-faults, cpu-migrations, etc.) on any system that runs Linux. As of mid 2023, the profiler supports x86, ARM, PowerPC64, UltraSPARC, and a few other CPU types.[^2] On such platforms, `perf` provides access to the hardware performance monitoring features, for example, performance counters. More information about Linux `perf` is available on its [wiki page](https://perf.wiki.kernel.org/index.php/Main_Page)[^1].

### How to configure it {.unlisted .unnumbered}

Installing Linux perf is very simple and can be done with a single command:

```bash
$ sudo apt-get install linux-tools-common linux-tools-generic linux-tools-`uname -r`
```

Also, consider changing the following defaults unless security is a concern:

```bash
# Allow kernel profiling and access to CPU events for unprivileged users
$ echo 0 | sudo tee /proc/sys/kernel/perf_event_paranoid
$ sudo sh -c 'echo kernel.perf_event_paranoid=0 >> /etc/sysctl.d/local.conf'
# Enable kernel modules symbols resolution for unprivileged users
$ echo 0 | sudo tee /proc/sys/kernel/kptr_restrict
$ sudo sh -c 'echo kernel.kptr_restrict=0 >> /etc/sysctl.d/local.conf'
```

### What you can do with it: {.unlisted .unnumbered}

Generally, Linux `perf` can do most of the same things that other profilers can do. Hardware vendors prioritize enabling their features in Linux `perf` so that by the time a new CPU is available on the market, `perf` already supports it. There are two main commands that most users will use. The first, `perf stat`, reports a count of specified performance events. The second, `perf record`, profiles an application or system in sampling mode and this is often followed by `perf report` to generate a report from the sampling data.

The output of the `perf record` command is a raw dump of samples. Many tools, built on top of Linux `perf`, parse raw dump files and provide new analysis types. Here are the most notable ones:

- Flame graphs, discussed in [@sec:secFlameGraphs].
- [KDAB Hotspot](https://github.com/KDAB/hotspot),[^3] a tool that visualizes Linux `perf` data with an interface very similar to Intel VTune. If you have worked with Intel VTune, KDAB Hotspot will seem very familiar to you.
- Netflix [Flamescope](https://github.com/Netflix/flamescope).[^4] This tool displays a heat map of sampled events over application runtime. You can observe different phases and patterns in the behavior of a workload. Netflix engineers found some very subtle performance bugs using this tool. Also, you can select a time range on the heat map and generate a flame graph for that time range.

### What you cannot do with it: {.unlisted .unnumbered}

Linux perf is a command-line tool and lacks a GUI, which makes it hard to filter data, observe how the workload behaviour changes over time, zoom into a portion of the runtime, etc. There is a limited console output provided through the `perf report` command, which is fine for quick analysis, although not as convenient as other GUI profilers. Luckily, as we just mentioned, there are GUI tools that can postprocess and visualize the raw output of Linux `perf`.

[^1]: Linux perf wiki - [https://perf.wiki.kernel.org/index.php/Main_Page](https://perf.wiki.kernel.org/index.php/Main_Page).
[^2]: RISCV is not supported yet as a part of the official kernel, although custom tools from vendors exist.
[^3]: KDAB Hotspot - [https://github.com/KDAB/hotspot](https://github.com/KDAB/hotspot).
[^4]: Netflix Flamescope - [https://github.com/Netflix/flamescope](https://github.com/Netflix/flamescope).