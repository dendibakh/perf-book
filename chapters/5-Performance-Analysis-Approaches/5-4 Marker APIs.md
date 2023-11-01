### Using Marker APIs {#sec:MarkerAPI}

In certain scenarios, we might be interested in analyzing performance of a specific code region, not an entire application. This can be a situation when you're developing a new piece of code and want to focus just on that code. Naturally, you would like to track optimization progress and capture additional performance data that will help you along the way. Most performance analysis tools provide specific *marker APIs* that let you do that. Here are a few examples:

* Likwid has `LIKWID_MARKER_START / LIKWID_MARKER_STOP` macros.
* Intel VTune has `__itt_task_begin / __itt_task_end` functions.
* AMD uProf has `amdProfileResume / amdProfilePause` functions.

Such a hybrid approach combines benefits of instrumentation and performance events couting. Instead of measuring the whole program, marker APIs allow us to attribute performance statistics to code regions (loops, functions) or functional piecies (remote procedure calls (RPCs), input events, etc.). The quality of the data you get back can easily justify the effort. While chasing performance bug that happens only with a specific type of RPCs, you can enable monitoring just for that type of RPC.

Below we provide a very basic example of using [libpfm4](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/),[^1] one of the popular Linux libraries for collecting performance monitoring events. It is built on top of the Linux `perf_events` subsystem, which lets you access performance event counters directly. The `perf_events` subsystem is rather low-level, so the `libfm4` package is useful here, as it adds both a discovery tool for identifying available events on your CPU, and a wrapper library around the raw `perf_event_open` system call. [@lst:LibpfmMarkerAPI] shows how one can use `libpfm4` to instrument the `render` function of the [C-Ray](https://openbenchmarking.org/test/pts/c-ray)[^2] benchmark.

Listing: Using libpfm4 marker API on the C-Ray benchmark

~~~~ {#lst:LibpfmMarkerAPI .cpp}
+#include <perfmon/pfmlib.h>
+#include <perfmon/pfmlib_perf_event.h>
...
/* render a frame of xsz/ysz dimensions into the provided framebuffer */
void render(int xsz, int ysz, uint32_t *fb, int samples) {
   ...
+  pfm_initialize();
+  struct perf_event_attr perf_attr;
+  memset(&perf_attr, 0, sizeof(perf_attr));
+  perf_attr.size = sizeof(struct perf_event_attr);
+  perf_attr.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | 
+                          PERF_FORMAT_TOTAL_TIME_RUNNING | PERF_FORMAT_GROUP;
+   
+  pfm_perf_encode_arg_t arg;
+  memset(&arg, 0, sizeof(pfm_perf_encode_arg_t));
+  arg.size = sizeof(pfm_perf_encode_arg_t);
+  arg.attr = &perf_attr;
+   
+  pfm_get_os_event_encoding("instructions", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  int leader_fd = perf_event_open(&perf_attr, 0, -1, -1, 0);
+  pfm_get_os_event_encoding("cycles", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  int event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+  pfm_get_os_event_encoding("branches", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+  pfm_get_os_event_encoding("branch-misses", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+
+  struct read_format { uint64_t nr, time_enabled, time_running, values[4]; };
+  struct read_format before, after;

  for(j=0; j<ysz; j++) {
    for(i=0; i<xsz; i++) {
      double r = 0.0, g = 0.0, b = 0.0;
+     // capture counters before ray tracing
+     read(event_fd, &before, sizeof(struct read_format));

      for(s=0; s<samples; s++) {
        struct vec3 col = trace(get_primary_ray(i, j, s), 0);
        r += col.x;
        g += col.y;
        b += col.z;
      }
+     // capture counters after ray tracing
+     read(event_fd, &after, sizeof(struct read_format));

+     // save deltas in separate arrays
+     nanosecs[j * xsz + i] = after.time_running - before.time_running;
+     instrs  [j * xsz + i] = after.values[0] - before.values[0];
+     cycles  [j * xsz + i] = after.values[1] - before.values[1];
+     branches[j * xsz + i] = after.values[2] - before.values[2];
+     br_misps[j * xsz + i] = after.values[3] - before.values[3];

      *fb++ = ((uint32_t)(MIN(r * rcp_samples, 1.0) * 255.0) & 0xff) << RSHIFT |
              ((uint32_t)(MIN(g * rcp_samples, 1.0) * 255.0) & 0xff) << GSHIFT |
              ((uint32_t)(MIN(b * rcp_samples, 1.0) * 255.0) & 0xff) << BSHIFT;
  } }
+ // aggregate statistics and print it
  ...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this code example, we first initialize `libpfm` library and configure performance events and the format that we will use to read them. In the C-Ray benchmark, the `render` function is only called once. In your own code, be carefull about not doing `libpfm` initialization multiple times. Then, we choose the code region we want to analyze, in our case it is a loop with a `trace` function call inside. We surround this code region with two `read` system calls that will capture values of performance counters before and after the loop. Next, we save the deltas for later processing, in this case, we aggregated (code is not shown) it by calculating average, 90th percentile and maximum values. Running it on an Intel Alderlake-based machine, we've got the output shown below. Root priviledges are not required, but `/proc/sys/kernel/perf_event_paranoid` should be set to less than 1. When reading counters from inside a thread, the values are for that thread alone. It can optionally include kernel code that ran and was attributed to the thread.

```bash
$ ./c-ray-f -s 1024x768 -r 2 -i sphfract -o output.ppm
Per-pixel ray tracing stats:
                      avg         p90         max
-------------------------------------------------
nanoseconds   |      4571 |      6139 |     25567
instructions  |     71927 |     96172 |    165608
cycles        |     20474 |     27837 |    118921
branches      |      5283 |      7061 |     12149
branch-misses |        18 |        35 |       146
```

Remember, that the instrumentation that we added measures the per-pixel ray tracing stats. Multiplying average numbers by the number of pixels (`1024x768`) should give us roughly the total stats for the program. A good sanity check in this case is to run `perf stat` and compare the overall C-Ray statistics for the performance events that we've collected.

The C-ray benchmark primarily stresses the floating-point performance of a CPU core, which generally should not cause high variance in the measuments, in other words, we expect all the measurements to be very close to each other. However, we see that it's not the case, as p90 values are 1.33x average numbers and max is sometimes 5x slower than the average case. The most likely explanation here is that for some pixels the algorithm hits a corner case, executes more instructions and subsequently runs longer. But it's always good to confirm the hypothesis by studying the source code or extending the instrumentation to capture more data for the "slow" pixels.

The additional instrumentation code showed in [@lst:LibpfmMarkerAPI] causes 17% overhead, which is OK for local experiments, but quite high to run in production. Most large distributed systems aim for less than 1% overhead, and for some up to 5% can be tolerable, but it's unlikely that users would be happy with 17% slowdown. Managing the overhead of your instrumentation is critical, especially if you choose to enable it in production environment.

Overhead is usefully calculated as occurence rate per unit of time or work (RPC, database query, loop iteration, etc.). If a system call on our system is roughly 1.6 microseconds of CPU time, and we do it twice for each pixel (iteration of the outer loop), the overhead is 3.2 microseconds of CPU time per pixel.

There are many strategies to bring the overhead down. As a general rule, your instrumentation should always have a fixed cost, e.g., a deterministic syscall, but not a list traversal or dynamic memory allocation, otherwise it will interfere with the measurements. The instumentation code has three logical parts: collecting the information, storing it, and reporting it. To lower the overhead of the first part (collection), we can decrease the sampling rate, e.g. sample each 10th RPC and skip the rest. For a long-running application, performance can be monitored with a relatively cheap random sampling - randomly select which events to observe. These methods sacrifice collection accuracy but still provide a good estimate of the overall performance characteristics while incurring a very low overhead.

For the second and third parts (storing and aggregating), the recommendation is to only collect, processes, and retain only much data as you need to understand the performance of the system. You can avoid storing every sample in memory by using "online" algorithms for calculating mean, variance, min, max and other metrics. This will drastically reduce the memory footprint of the instrumentation. For instance, variance and standard deviation can be calculated using Knuth's online-variance algorithm. A good implementation[^3] uses less than 50 bytes of memory.

For long routines, you can collect counters at the beginning, end, and some parts in the middle. Over consequtive runs, you can binary search for the part of the routine that performs poorest and optimize it. Repeat this until all the poorly-performing spots are removed. If tail latency is of a primary concern, emitting log messages on a particularly slow run can provide useful insights.

In the [@lst:LibpfmMarkerAPI], we collected 4 events simultaneously, though the CPU has 6 programmable counters. You can open up additional groups with different sets of events enabled. The kernel will select different groups to run at a time. The `time_enabled` and `time_running` fields indicate the multiplexing. They are both durations in nanoseconds. The `time_enabled` field indicates how many nanoseconds the event group has been enabled. The `time_running` indicates how much of that enabled time the events were actually collecting. If you had two event groups enabled simultaneously that couldn't fit together on the HW counters, you might see them both converge to `time_running = 0.5 * time_enabled`. Scheduling in general is complicated so verify before depending on your exact scenario.

Capturing multiple events simultaneously allows to calculate various metrics that we discussed in Chapter 4. For example, capturing `INSTRUCTIONS_RETIRED` and `UNHALTED_CLOCK_CYCLES` enables us to measure IPC. We can observe the effects of frequency scaling by comparing CPU cycles (`UNHALTED_CORE_CYCLES`) vs the fixed-frequency reference clock (`UNHALTED_REFERENCE_CYCLES`). It is possible to detect when the thread wasn't running by requesting CPU cycles consumed (`UNHALTED_CORE_CYCLES`, only counts when the thread is running) and comparing against wall-clock time. Also, we can normalize the numbers to get the event rate per second/clock/instruction. For instance, measuring `MEM_LOAD_RETIRED.L3_MISS` and `INSTRUCTIONS_RETIRED` we can get the `L3MPKI` metric. As you can see, the setup is very flexible.

The important property of grouping events is that the counters will be available atomically under the same `read` system call. These atomic bundles are very useful. First, it allows us to correlate events within each group. Say we measure IPC for a region of code, and found that it is very low. In this case, we can pair two events (instructions and cycles) with a third one, say L3 cache misses, to check if it contributes to a low IPC that we're dealing with. If it doesn't, we continue factor analysis using other events. Second, event grouping helps to mitigate bias in case a workload has different phases. Since all the events within a group are measured at the same time, they always capture the same phase.

In some scenarios, instrumentation may become a part of a functionality or a feature. For example, a developer can implement an instrumentation logic that detects decrease in IPC (e.g. when there is a busy sibling HW thread running) or decreasing CPU frequency (e.g. system throttling due to heavy load). When such event occurs, application automatically defers low-priority work to compensate for the temporarily increased load.

[^1]: libpfm4 - [https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/)

[^2]: C-Ray benchmark - [https://openbenchmarking.org/test/pts/c-ray](https://openbenchmarking.org/test/pts/c-ray)

[^3]: Accurately computing running variance - [https://www.johndcook.com/blog/standard_deviation/](https://www.johndcook.com/blog/standard_deviation/)
