## Code instrumentation
Probably the first approach for doing performance analysis ever invented is Code Instrumenta-
tion. It is a technique that inserts extra code into a program to collect runtime information.
Listing 6 shows the simplest example of inserting printf statements at the beginning of the
function to count the number of times this function was called. I think every programmer in
the world did it at some point at least once. This method provides very detailed information
when you need specific knowledge about the execution of the program. Code instrumentation
allows us to track any information about every variable in the program.

Instrumentation based profiling methods are mostly used on a macro level, not on the micro(low)
level. Using such a method often yields the best insight when optimizing big pieces of code
because you can use a top-down approach (instrumenting the main function then drilling down
to its callees) of locating performance issues. While code instrumentation is not very helpful
in the case of small programs, it gives the most value and insight by letting developers observe
the architecture and flow of an application. This technique is especially helpful for someone
working with an unfamiliar codebase.

It’s also worth mentioning that code instrumentation shines in complex systems with many
different components that react differently based on inputs or over time. Sampling techniques
(discussed in section 5.4) squash that valuable information, not allowing us to detect abnormal
behaviors. For example, in games, usually, there is a renderer thread, physics thread, animations
thread, etc. Instrumenting such big modules help to reasonably quickly to understand what
module is the source of issues. As sometimes, optimizing is not only a matter of optimizing
code but also data. For example, rendering is too slow because of uncompressed mesh, or
physics are too slow because of too many objects in the scene.

The technique is heavily used in real-time scenarios, such as video games and embedded
development. Many profilers70 mix up instrumentation with other techniques discussed in this
chapter (tracing, sampling).

While code instrumentation is powerful in many cases, it does not provide any information
about how the code executes from the OS or CPU perspective. For example, it can’t give you
information about how often the process was scheduled in and out from the execution (known
by the OS) or how much branch mispredictions occurred (known by the CPU). Instrumented
code is a part of an application and has the same privileges as the application itself. It runs in
userspace and doesn’t have access to the kernel.

But more importantly, the downside of this technique is that every time something new needs
to be instrumented, say another variable, recompilation is required. This can become a burden
to an engineer and increase analysis time. It is not all downsides, unfortunately. Since usually,
you care about hot paths in the application, you’re instrumenting the things that reside in the
performance-critical part of the code. Inserting instrumentation code in a hot piece of code
might easily result in a 2x slowdown of the overall benchmark71. Finally, by instrumenting
the code, you change the behavior of the program, so you might not see the same effects you
saw earlier.

All of the above increases time between experiments and consumes more development time,
which is why engineers don’t manually instrument their code very often these days. However,
automated code instrumentation is still widely used by compilers. Compilers are capable of
automatically instrumenting the whole program and collect interesting statistics about the
execution. The most widely known use cases are code coverage analysis and Profile Guided
Optimizations (see section 7.7).

When talking about instrumentation, it’s important to mention binary instrumentation
techniques. The idea behind binary instrumentation is similar but done on an already
built executable file as opposed to on a source code level. There are two types of binary
instrumentation: static (done ahead of time) and dynamic (instrumentation code inserted on-
demand as a program executes). The main advantage of dynamic binary instrumentation is that
it does not require program recompilation and relinking. Also, with dynamic instrumentation,
one can limit the amount of instrumentation to only interesting code regions, not the whole
program.

Binary instrumentation is very useful in performance analysis and debugging. One of the most
popular tools for binary instrumentation is Intel Pin72 tool. Pin intercepts the execution of
the program in the occurrence of an interesting event and generates new instrumented code
starting at this point in the program. It allows collecting various runtime information, for
example:
• instruction count and function call counts.
• intercepting function calls and execution of any instruction in an application.
• allows “record and replay” the program region by capturing the memory and HW registers
state at the beginning of the region.

Like code instrumentation, binary instrumentation only allows instrumenting user-level code
and can be very slow.


### Using Marker APIs for Attribution
You can choose the places where you add explicit instrumentation to usefully
mark your code. You can mark parts of your code to attribute CPU work done
against elements at the level of code (loops, branches, etc.) or load (input
events, types of RPCs, etc.). The quality of the data you get back can easily
justify the effort.

Managing the overhead of your instrumentation will be critical. There are three
parts: collecting the information, storing it, and reporting it. Overhead is
usefully calculated as rates. Rates per unit of either time or element (RPC,
loop iteration, etc.). Each collection should have a fixed cost (e.g., a
syscall, but not a list traversal) and its overhead is that cost times the rate.
For example, a system call is roughly 1.6 microseconds of CPU time, and if you collect
4 times per RPC, your overhead is 6.4 microseconds of CPU per RPC.

Collection overhead depends on how many times the API is called during the work.
Storage overhead is either linear or logarithmic to the collection rate times
the retentia

To control overhead and relevancy you can choose when to enable or record the
instrumentation. Random sampling gives you the overall character of your
performance, but emitting data (e.g., log message) on particularly slow runs
through some code can provide useful insight on tail latency.

Explicit instrumentation makes a lot of sense for two different scenarios: when
you're developing your code and are already going to recompile it often and when
you want the instrumentation around for monitoring during runtime. Some
instrumentation fits in both categories. Others you may want behind an `#ifdef`
or macro to leave off for production.


Once you've collected your measurements in your process, you'll have to get
that data back to you to analyze.  You have to be careful not to flood some
I/O system with too much performance data.  The application performance will sink and
the instrumentation will interfere too much with the runtime.

* Mark LOC for precise measurements
* Attribute events (cache misses, cycles) to specific regions of code
* Attribute the 'cost' of running the application to specific work.


% Using the APIs
For CPU usage, outside of wall-clock time (`clock_gettime(2)`), your best option
on Linux is the `perf_events` subsystem. It lets you read performance event
counters directly.  The subsystem is rather low-level, so the `perfmon2-libfm4`
package is useful here, as it adds both a discovery tool for identifying
available events on your CPU's PMU, and a wrapper library around the raw `perf_event_open(2)`
system call.  Here's an example that (poorly) benchmarks `sqrt(3)`:
```c
#include <assert.h>
#include <math.h>
#include <perfmon/pfmlib.h>
#include <perfmon/pfmlib_perf_event.h>

// The flags to perf_event_open() determine which fields are returned
// from the resulting FD.
struct read_format { uint64_t nr, time_enabled, time_running, values[2]; };
void require_pfm(int value) { assert(value == PFM_SUCCESS); }
void require_nonneg(int value) { assert(value >= 0); }

int main(int argc, char **argv) {
   double value = uintptr_t(argv) % 50000;  // Avoid compiler precomputation
   int event_fd;
   perf_event_attr  perf_attr{};
   perf_attr.size = sizeof(perf_event_attr);
   perf_attr.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING | PERF_FORMAT_GROUP;

   pfm_perf_encode_arg_t perf_setup{};
   perf_setup.size = sizeof(pfm_perf_encode_arg_t);
   perf_setup.attr = &perf_attr;

   require_pfm(pfm_initialize());
   // See the output of `showevtinfo`, which comes as an example program with perfmon2-libpfm4
   require_pfm(pfm_get_os_event_encoding("INSTRUCTIONS_RETIRED", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &perf_setup));
   require_nonneg((event_fd = perf_event_open(&perf_attr, 0, -1, -1, 0)));
   require_pfm(pfm_get_os_event_encoding("LLC_MISSES", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &perf_setup));
   require_nonneg((event_fd = perf_event_open(&perf_attr, 0, -1, event_fd, 0)));

   read_format cur, prior;
   require_nonneg(read(event_fd, &prior, sizeof(read_format)));

   // code being benchmarked
   value = sqrt(value);

   require_nonneg(read(event_fd, &cur, sizeof(read_format)));

   printf("Got value %lu for retired_instructions.  ", cur.values[0] - prior.values[0]);
   printf("Got value %lu for llc_misses.  ", cur.values[1] - prior.values[1]);
   printf("On-CPU time was %lu nanosecs\n", cur.time_running - prior.time_running);

   return 0;
}
```

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


