## What Is not Discussed in this Book?

System performance depends on different components: CPU, DRAM, I/O and network devices, etc. Applications may benefit from tuning various components of the system, depending on where a bottleneck is. In general, engineers should analyze the performance of the whole system. However, the biggest factor in systems performance is its heart, the CPU. This is why this book primarily focuses on performance analysis from a CPU perspective. We also discuss memory subsystem quite extensively, but we don't exlore I/O and network performance.

Likewise, the software stack includes many layers, e.g., firmware, BIOS, OS, libraries, and the source code of an application. But since most of the lower layers are not under our direct control, the primary focus will be made on the source code level.

The scope of the book does not go beyond a single CPU socket, so we will not discuss optimization techniques for distributed, NUMA, and heterogeneous systems. Offloading computations to accelerators (GPU, FPGA, etc.) using solutions like OpenCL and openMP is not discussed in this book. 

I tried to make this book to be applicable to most modern CPUs, including Intel, AMD, Apple, and other ARM-based processors. I'm very sorry if it doesn't cover your favorite architecture. Nevertheless, many of the principles discussed in this book apply well to other processors. Similarly, most examples in this book were run on Linux, but again, most of the time it doesn't matter since the same techniques benefit applications that run on Windows and macOS operating systems.

Code snippets in this book are written in C, C++, or x86 assembly languages, but to a large degree, ideas from this book can be applied to other languages that are compiled to native code like Rust, Go, and even Fortran. Since this book targets user-mode applications that run close to the hardware, we will not discuss managed environments, e.g., Java. 

Finally, the author assumes that readers have full control over the software that they develop, including the choice of libraries and compilers they use. Hence, this book is not about tuning purchased commercial packages, e.g., tuning SQL database queries.

