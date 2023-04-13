### Using Marker APIs

In certain scenarios, we might be interested in analyzing performance of a specific code region, not an entire application. This can be a situation when you're developing a new piece of code and want to focus just on that code. Naturally, you would like to track optimization progress and capture additional performance data that will help you along the way. Most performance analysis tools provide specific *marker APIs* that let you do that. Here are a few examples:

* Likwid has `LIKWID_MARKER_START / LIKWID_MARKER_STOP` macros.
* Intel VTune has `__itt_task_begin / __itt_task_end` functions.
* AMD uProf has `amdProfileResume / amdProfilePause` functions.

Such a hybrid approach combines benefits of instrumentation and performance events couting. Instead of measuring the whole program, marker APIs allow us to attribute performance statistics to code regions (loops, functions) or functional piecies (remote procedure calls (RPCs), input events, etc.). The quality of the data you get back can easily justify the effort. While chasing performance bug that happens only with a specific type of RPCs, you can enable monitoring just for that type of RPC.

Below we provide a very basic example of using [libpfm4](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/)[^1], one of the popular Linux libraries for collecting performance monitoring events. It is built on top of the Linux `perf_events` subsystem, which lets you access performance event counters directly. The `perf_events` subsystem is rather low-level, so the `libfm4` package is useful here, as it adds both a discovery tool for identifying available events on your CPU, and a wrapper library around the raw `perf_event_open` system call. [@lst:LibpfmMarkerAPI] shows how one can use `libpfm4` to instrument the `render` function of the [C-Ray](https://openbenchmarking.org/test/pts/c-ray)[^2] benchmark.

Listing: Using libpfm4 marker API on the C-Ray benchmark

~~~~ {#lst:LibpfmMarkerAPI .cpp}
+#include <perfmon/pfmlib.h>
+#include <perfmon/pfmlib_perf_event.h>
+  
int main(int argc, char **argv) {
   // ...
   load_scene(infile);
 
+  pfm_initialize();
+
+  struct perf_event_attr perf_attr;
+  memset(&perf_attr, 0, sizeof(perf_attr));
+  perf_attr.size = sizeof(struct perf_event_attr);
+  perf_attr.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | 
+                          PERF_FORMAT_TOTAL_TIME_RUNNING | PERF_FORMAT_GROUP;
+   
+  pfm_perf_encode_arg_t arg;
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
-  start_time = get_msec();
+  struct read_format { uint64_t nr, time_enabled, time_running, values[4]; };
+  struct read_format cur, prior;
+  read(event_fd, &prior, sizeof(struct read_format));
   render(xres, yres, pixels, rays_per_pixel);
-  rend_time = get_msec() - start_time;
+  read(event_fd, &cur, sizeof(struct read_format));
 
   /* output statistics to stderr */
-  fprintf(stderr, "Rendering took: %lu seconds (%lu milliseconds)\n", rend_time / 1000, rend_time);
+  fprintf(stderr, "Rendering took: %lu nanosecs of CPU time\n", cur.time_running - prior.time_running);
+  fprintf(stderr, "instructions: %lu\n", cur.values[0] - prior.values[0]);
+  fprintf(stderr, "cycles: %lu\n", cur.values[1] - prior.values[1]);
+  fprintf(stderr, "branches: %lu\n", cur.values[2] - prior.values[2]);
+  fprintf(stderr, "branch-misses: %lu\n", cur.values[3] - prior.values[3]);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We run it on the Intel Alderlake-based machine and here is the output we've got, numbers that you see might differ. 

```bash
$ ./c-ray-f -s 1024x768 -r 2 -i sphfract -o output.ppm
Rendering took: 3408273087 nanosecs of CPU time
instructions: 56583325716
cycles: 15967087210
branches: 4154308095
branch-misses: 14479489

# counts are very similar to the output of:
$ perf stat -e instructions,cycles,branches,branch-misses -- ./c-ray-f -s 1024x768 -r 2 -i sphfract -o output.ppm
```

TODO: should we take a better representable example? The one that would show aggregating results from multiple runs of a function? We can also measure the overhead.

The results are very close to the output of `perf stat` command, because, the most time is spent inside `render` function. 

**Overhead**

Managing the overhead of your instrumentation is critical. There are three parts: collecting the information, storing it, and reporting it. Overhead is usefully calculated as rates. Rates per unit of either time or element (RPC, loop iteration, etc.). Each collection should have a fixed cost (e.g., a syscall, but not a list traversal) and its overhead is that cost times the rate. For example, a system call is roughly 1.6 microseconds of CPU time, and if you collect 4 times per RPC, your overhead is 6.4 microseconds of CPU per RPC.

Collection overhead depends on how many times the API is called during the work. Storage overhead is either linear or logarithmic to the collection rate times the retentia

To control overhead and relevancy you can choose when to enable or record the instrumentation. Random sampling gives you the overall character of your performance, but emitting data (e.g., log message) on particularly slow runs through some code can provide useful insight on tail latency.

**Usage scenarios**

TODO: you can also leave it enabled in production if the overhead is not too big.

Explicit instrumentation makes a lot of sense for two different scenarios: when you're developing your code and are already going to recompile it often and when you want the instrumentation around for monitoring during runtime. Some instrumentation fits in both categories. Others you may want behind an `#ifdef` or macro to leave off for production.

Once you've collected your measurements in your process, you'll have to get that data back to you to analyze.  You have to be careful not to flood some I/O system with too much performance data.  The application performance will sink and the instrumentation will interfere too much with the runtime.

* Mark LOC for precise measurements
* Attribute events (cache misses, cycles) to specific regions of code
* Attribute the 'cost' of running the application to specific work.

#### Example: using libfm4



TODO: describe multiplexing in case we specify more events than physical counters.
TODO: Lally: Measuring blocks of counters together can calculate useful things! For example, `INSTRUCTIONS_RETIRED / UNHALTED_CLOCK_CYCLES = IPC`.
Grouping those two events together with a third one, say L3 cache misses, will aid your factor analysis. In the event of low IPC, you will be able to observe which other factor may contribute to the poor code performance.

Use `perf_event_open(2)` to get a file descriptor representing the counters, then use `read(2)` to read the counters whenever you want. When reading it from inside the thread, the counters are for that thread alone. This can optionally include kernel code that ran and was attributed to the thread. The returned performance counter values are just `int64` event counts.

The difference in event counts over a region of code is the number of events that occurred during that region, in that thread. That difference divided by the time taken is the event rate. You can ask for up to 3 counters simultaneously in one file descriptor. They will available atomically under the same `read(2)` system call. These atomic bundles are very useful. 

TODO: root priviledges are not required.
Repeatedly running the example above (you will probably have to 0 to `/proc/sys/kernel/perf_event_paranoid` to  make it work).

**Interpreting the data**

You can compensate for the scheduler by requesting CPU cycles consumed (e.g., `UNHALTED_CORE_CYCLES`) and comparing against wall-clock time to detect when the thread wasn't running. You can similarly see the effects of frequency stepping by comparing CPU cycles (`UNHALTED_CORE_CYCLES`) vs the fixed-frequency reference clock (`UNHALTED_REFERENCE_CYCLES`).

TODO: describe possibility to implement adaptive mechanisms. For example, detect throttling and defer some low-priority work.

In the example, we only printed the difference between the beginning and end. But it's more flexible to save the raw counter values instead of differences. In post-processing you can choose the intervals you care about, and not be sensitive to the ones you thought you needed when adding the instrumentation.

% Interval Estimation
<deleted; summarized & moved up>

% Grouped Counter techniques
<moved up>
   
% Getting the data out of process
<deleted>
 
% Aggregate Statistics Solutions
<deleted>

[^1]: libpfm4 - [https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/)
[^2]: C-Ray benchmark - [https://openbenchmarking.org/test/pts/c-ray](https://openbenchmarking.org/test/pts/c-ray)