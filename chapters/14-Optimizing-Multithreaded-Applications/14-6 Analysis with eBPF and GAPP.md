---
typora-root-url: ..\..\img
---

## Analysis with eBPF and GAPP {#sec:secEBPF}

Linux supports a variety of thread synchronization primitives – mutexes, semaphores, condition variables, etc. The kernel supports these thread primitives via the `futex` system call. Therefore, by tracing the execution of the `futex` system call in the kernel while gathering useful metadata from the threads involved, contention bottlenecks can be more readily identified. Linux provides kernel tracing/profiling tools that make this possible, none more powerful than [Extended Berkley Packet Filter](https://prototype-kernel.readthedocs.io/en/latest/bpf/)[^22] (eBPF).

eBPF is based around a sandboxed virtual machine running in the kernel that allows the execution of user-defined programs safely and efficiently inside the kernel. The user-defined programs can be written in C and compiled into BPF bytecode by the [BCC compiler](https://github.com/iovisor/bcc)[^23] in preparation for loading into the kernel VM. These BPF programs can be written to launch upon the execution of certain kernel events and communicate raw or processed data back to userspace via a variety of means. 

The open0source community has provided many eBPF programs for general use. One such tool is the [Generic Automatic Parallel Profiler](https://github.com/RN-dev-repo/GAPP/) (GAPP), which helps to track multithreaded contention issues. GAPP uses eBPF to track contention overhead of a multithreaded application by ranking the criticality of identified serialization bottlenecks, collects stack traces of threads that were blocked and the one that caused the blocking. The best thing about GAPP is that it does not require code changes, expensive instrumentation, or recompilation. Creators of the GAPP profiler were able to confirm known bottlenecks and also expose new, previously unreported bottlenecks on [Parsec 3.0 Benchmark Suite](https://parsec.cs.princeton.edu/index.htm)[^24]and some large open-source projects. [@GAPP]

[^22]: eBPF docs - [https://prototype-kernel.readthedocs.io/en/latest/bpf/](https://prototype-kernel.readthedocs.io/en/latest/bpf/)
[^23]: BCC compiler - [https://github.com/iovisor/bcc](https://github.com/iovisor/bcc)
[^24]: Parsec 3.0 Benchmark Suite - [https://parsec.cs.princeton.edu/index.htm](https://parsec.cs.princeton.edu/index.htm)
