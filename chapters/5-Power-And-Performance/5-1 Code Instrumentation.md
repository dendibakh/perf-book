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
If you explicitly instrument places in your code, you make them amenable to attribution
for CPU usage, and can attribute different workloads to different CPU usages. For CPU usage,
outside of wall-clock time (`clock_gettime(2)`), your best option on Linux is
`perf_event_open(2)`.

The `perf_events` subsystem lets you read performance event counters directly. Use
`perf_event_open(2)` to get a file descriptor representing the counters, then use
`read(2)` to read the counters. You can `read(2)` the file descriptor repeatedly to get
the counter values at different times. When reading it from inside the thread, the
counters are for that thread alone. This can optionally include kernel time attributed to
the thread. The returned performance counter values are just `int64` event counts.

The difference in event counts over a region of code is the number of events that occurred
during that region, in that thread. That difference divided by the time taken is the event
rate. You can ask for up to 3 counters simultaneously in one file descriptor. They will
available atomically under the same `read(2)` system call.

Using a 




* Mark LOC for precise measurements
* Attribute events (cache misses, cycles) to specific regions of code
* Attribute the 'cost' of running the application to specific work.


