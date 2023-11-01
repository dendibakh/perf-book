---
typora-root-url: ..\..\img
---

## Tracing

Tracing is conceptually very similar to instrumentation yet slightly different. Code instrumentation assumes that the user can orchestrate the code of their application. On the other hand, tracing relies on the existing instrumentation of a program's external dependencies. For example, the `strace` tool enables us to trace system calls and can be thought of as the instrumentation of the Linux kernel. Intel Processor Traces (see Appendix D) enables you to log instructions executed by the program and can be thought of as the instrumentation of the CPU. Traces can be obtained from components that were appropriately instrumented in advance and are not subject to change. Tracing is often used as the black-box approach, where a user cannot modify the code of the application, yet they want insights on what the program is doing behind the scenes.

An example of tracing system calls with the Linux `strace` tool is provided in [@lst:strace], which shows the first several lines of output when running the `git status` command. By tracing system calls with `strace` it's possible to know the timestamp for each system call (the leftmost column), its exit status, and the duration of each system call (in the angle brackets).

Listing: Tracing system calls with strace.
		
~~~~ {#lst:strace .bash}
$ strace -tt -T -- git status
17:46:16.798861 execve("/usr/bin/git", ["git", "status"], 0x7ffe705dcd78 
                  /* 75 vars */) = 0 <0.000300>
17:46:16.799493 brk(NULL)               = 0x55f81d929000 <0.000062>
17:46:16.799692 access("/etc/ld.so.nohwcap", F_OK) = -1 ENOENT 
                  (No such file or directory) <0.000063>
17:46:16.799863 access("/etc/ld.so.preload", R_OK) = -1 ENOENT 
                  (No such file or directory) <0.000074>
17:46:16.800032 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3 
                  <0.000072>
17:46:16.800255 fstat(3, {st_mode=S_IFREG|0644, st_size=144852, ...}) = 0 
                  <0.000058>
17:46:16.800408 mmap(NULL, 144852, PROT_READ, MAP_PRIVATE, 3, 0) 
                  = 0x7f6ea7e48000 <0.000066>
17:46:16.800619 close(3)                = 0 <0.000123>
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The overhead of tracing very much depends on what exactly we try to trace. For example, if we trace a program that almost never makes system calls, the overhead of running it under `strace` will be close to zero. On the other hand, if we trace a program that heavily relies on system calls, the overhead could be very large, e.g. 100x.[^1] Also, tracing can generate a massive amount of data since it doesn't skip any sample. To compensate for this, tracing tools 
provide filters that enable you to restrict data collection to a specific time slice or for a specific section of code.

Usually, tracing similar to instrumentation is used for exploring anomalies in the system. For example, you may want to determine what was going on in an application during a 10s period of unresponsiveness. As you will see later, sampling methods are not designed for this, but with tracing, you can see what lead to the program being unresponsive. For example, with Intel PT, you can reconstruct the control flow of the program and know exactly what instructions were executed.

Tracing is also very useful for debugging. Its underlying nature enables "record and replay" use cases based on recorded traces. One such tool is the Mozilla [rr](https://rr-project.org/)[^2] debugger, which performs record and replay of processes, supports backwards single stepping and much more. Most of the tracing tools are capable of decorating events with timestamps, which allows us to have a correlation with external events that were happening during that time. That is, when we observe a glitch in a program, we can take a look at the traces of our application and correlate this glitch with what was happening in the whole system during that time.

[^1]: An article about `strace` by B. Gregg - [http://www.brendangregg.com/blog/2014-05-11/strace-wow-much-syscall.html](http://www.brendangregg.com/blog/2014-05-11/strace-wow-much-syscall.html)

[^2]: Mozilla rr debugger - [https://rr-project.org/](https://rr-project.org/).