### Using Marker APIs

TODO: describe that this is a hybrid approach, that uses code instrumentation but only for a specific code portion, not a whole program.

You can choose the places where you add explicit instrumentation to usefully mark your code. You can mark parts of your code to attribute CPU work done against elements at the level of code (loops, branches, etc.) or load (input events, types of RPCs, etc.). The quality of the data you get back can easily justify the effort.

Managing the overhead of your instrumentation will be critical. There are three parts: collecting the information, storing it, and reporting it. Overhead is usefully calculated as rates. Rates per unit of either time or element (RPC, loop iteration, etc.). Each collection should have a fixed cost (e.g., a syscall, but not a list traversal) and its overhead is that cost times the rate. For example, a system call is roughly 1.6 microseconds of CPU time, and if you collect 4 times per RPC, your overhead is 6.4 microseconds of CPU per RPC.

Collection overhead depends on how many times the API is called during the work. Storage overhead is either linear or logarithmic to the collection rate times the retentia

To control overhead and relevancy you can choose when to enable or record the instrumentation. Random sampling gives you the overall character of your performance, but emitting data (e.g., log message) on particularly slow runs through some code can provide useful insight on tail latency.

Explicit instrumentation makes a lot of sense for two different scenarios: when you're developing your code and are already going to recompile it often and when you want the instrumentation around for monitoring during runtime. Some instrumentation fits in both categories. Others you may want behind an `#ifdef` or macro to leave off for production.

Once you've collected your measurements in your process, you'll have to get that data back to you to analyze.  You have to be careful not to flood some I/O system with too much performance data.  The application performance will sink and the instrumentation will interfere too much with the runtime.

* Mark LOC for precise measurements
* Attribute events (cache misses, cycles) to specific regions of code
* Attribute the 'cost' of running the application to specific work.

% Using the APIs

For CPU usage, outside of wall-clock time (`clock_gettime(2)`), your best option on Linux is the `perf_events` subsystem. It lets you read performance event counters directly. The subsystem is rather low-level, so the `perfmon2-libfm4` package is useful here, as it adds both a discovery tool for identifying available events on your CPU's PMU, and a wrapper library around the raw `perf_event_open(2)` system call. Here's an example that (poorly) benchmarks `sqrt(3)`:

```cpp
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
```

```bash
$ ./c-ray-f -s 1024x768 -r 2 -i sphfract -o output.ppm
Rendering took: 3408273087 nanosecs of CPU time
instructions: 56583325716
cycles: 15967087210
branches: 4154308095
branch-misses: 14479489
```

TODO: describe multiplexing, in case we specify more events than physical counters.

Use `perf_event_open(2)` to get a file descriptor representing the counters,
then use `read(2)` to read the counters whenever you want. When reading it from
inside the thread, the counters are for that thread alone. This can optionally
include kernel code that ran and was attributed to the thread. The returned
performance counter values are just `int64` event counts.

The difference in event counts over a region of code is the number of events
that occurred during that region, in that thread. That difference divided by the
time taken is the event rate. You can ask for up to 3 counters simultaneously in
one file descriptor. They will available atomically under the same `read(2)`
system call. These atomic bundles are very useful. 

Repeatedly running the example above (you will probably have to 0 to `/proc/sys/kernel/perf_event_paranoid` to 
make it work), you will get something like:
```
Got value 39 for retired_instructions.  Got value 130 for llc_misses.  On-CPU time was 2209 nanosecs
Got value 39 for retired_instructions.  Got value 57 for llc_misses.  On-CPU time was 1868 nanosecs
Got value 39 for retired_instructions.  Got value 54 for llc_misses.  On-CPU time was 1732 nanosecs
```


You can compensate for the scheduler by requesting CPU cycles consumed (e.g.,
`UNHALTED_CORE_CYCLES`) and comparing against wall-clock time to detect when the
thread wasn't running. You can similarly see the effects of frequency stepping by
comparing CPU cycles (`UNHALTED_CORE_CYCLES`) vs the fixed-frequency reference clock
(`UNHALTED_REFERENCE_CYCLES`).

You can also correlate low IPC (`INSTRUCTIONS_RETIRED/UNHALTED_CORE_CYCLES`) to
events you believe dominate it (e.g., `LLC_MISSES`).


% Interval Estimation

Between two `read(2)` calls to read perf counters, you have some lines that
cause the counters to increase. It's more flexible to save the raw counter
values instead of differences.  In post-processing you can choose the intervals
you care about, and not be sensitive to the ones you thought you needed when
adding the instrumentation.  For example, if you have a loop:


```c
  // hacked up from the epoll(2) manpage
  // TODO: go back and add the right APIs for this.  Stubs ok for now.
  typedef snapshot_t uint64_t;
  struct perf_data_record {
      snapshot_t post_epoll, loop_iter_start, post_accept, loop_iter_finish;
      int nfds, n;
      bool listen_event;
  } snapshot;
  int counter_fd;
  
  for (;;) {
     nfds = epoll_wait(epollfd, events, MAX_EVENTS, -1);
     read(counter_fd, snapshot.post_epoll, 48)    // post_epoll
     
     if (nfds == -1) {
         perror("epoll_wait");
         exit(EXIT_FAILURE);
     }

     snapshot.nfds = nfds;
     for (n = 0; n < nfds; ++n) {
         read(counter_fd, snapshot.loop_iter_start, 48)   // loop_iter_start
         snapshot.n = n;
         if (events[n].data.fd == listen_sock) {
             snapshot.listen_event = true;
             conn_sock = accept(listen_sock,
                                (struct sockaddr *) &addr, &addrlen);
             read(counter_fd, snapshot.post_accept, 48)   // post_accept
             asssert (conn_sock == -1);
             setnonblocking(conn_sock);
             ev.events = EPOLLIN | EPOLLET;
             ev.data.fd = conn_sock;
             if (epoll_ctl(epollfd, EPOLL_CTL_ADD, conn_sock,
                         &ev) == -1) {
                 perror("epoll_ctl: conn_sock");
                 exit(EXIT_FAILURE);
             }
         } else {
             snapshot.listen_event = false;
             do_use_fd(events[n].data.fd);
         }
         read(counter_fd, snapshot.loop_iter_finish, 48)   // loop_iter_finish
     }
     write_snapshot(snapshot);
   }

```
  This instrumentation tells quite a story about the loop.  Set it up for L2 cache misses to start.
  This loop will write one snapshot per event from `epoll(2)`.  (We'll talk about what writing
  a snapshot means later, but for now imagine that it's going to a binary file with a big buffer that 
  you'll read in post-processing.)  Note that fields that aren't modified are preserved between writes.
  This is sueful for `snapshot.post_epoll`.
  
  Looking at just `snapshot.loop_iter_finish - snapshot.loop_iter_start` for the
  final iteration (`n==nfds-1`) for L2 misses and you'll see how many cache
  lines you're evicting (and waiting for) before blocking on `epoll(2)` again.
  Looking at the `snapshot.loop_iter_finish` for one snapshot and the
  `snapshot.post_epoll` of the next record indicates how many lines got evicted
  when blocked (if you have kernel-events turned on).
  
  Writing out the type of event (just whether it's `listen_event` here) indicates the breakdown. You
  can compare the `snapshot.loop_iter_finish-snapshot.loop_iter_start` intervals for each event
  and break down the impact of each kind of event. That can be in lines of cache evictions, clock cycles,
  TLB misses, etc.
  
  Similarly, the `post_accept-loop_iter_start` values when `listen_event==True` measure the cost
  of `accept(2)`.

% Grouped Counter techniques
 - Measuring blocks of counters together can calculate useful things!
 - INSTRUCTIONS_RETIRED vs UNHALTED_CLOCK_CYCLES gives you IPC.
 - Running those two against a third potential IPC factor (e.g. L2 misses) 
   is good enough for factor analysis.
   

% Getting the data out of process
 - Really, a big-ass `fwrite(3)` with a big-healthy `setbuf(3)` call works pretty well.
 - Mention IPC techniques or ring-buffer snapshotting to disk to minimize overhead/jitter.  Use a seqno.
 
% Aggregate Statistics Solutions
 - If you have a code block like:
 ```c
    void foo(int arg) {
        read(counter_fd, snapshot.foo_start, 48)
        [A,B,C] = work_required(arg)
        snapshot.arg = arg;
        snapshot.A = A;
        snapshot.B = B;
        snapshot.C = C;
        for (int i=0; i<A; i++) {
          do_work_a(i);
        }  
        for (int i=0; i<B; i++) {
          do_work_b(i);
        }  
        for (int i=0; i<C; i++) {
          do_work_c(i);
        }
        read(counter_fd, snapshot.foo_end, 48)
        write_snapshot(snapshot)

    }
 ```
   You can solve for counter values for `do_work_a`, `do_work_b`, and `do_work_c`.  This is from the SVD (Singular 
   Value Decompostion)  pseudo-inverse.  The counter values are $x_1, x_2, x_3$ where $D$ is `foo_end-foo_start` 
   and the loop structure has this relationship:
   
    $ Ax_1 + Bx_2 + Cx_3 = D $ 

   Each snapshot forms a row in a matrix $M$ of rows $[A, B, C, D]$ and with a few of
   them (at least 3, but get more for better variety of values), you can estimate $x_1, x_2, x_3$ by the estimate $M`$` 
   you get from the SVD pseudoinverse. 


