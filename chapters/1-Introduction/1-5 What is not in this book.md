---
typora-root-url: ..\..\img
---

## What is not in this book?

[TODO]: second edition talks much more about system performance, especially memory subsystem. Also, we talk about compilers.

System performance depends on different components: CPU, OS, memory, I/O  devices, etc. Applications could benefit from tuning various components of the system. In general, engineers should analyze the performance of the whole system. However, the biggest factor in systems performance is its heart, the CPU. This is why this book primarily focuses on performance analysis from a CPU perspective, occasionally touching on OS and memory subsystems.

The scope of the book does not go beyond a single CPU socket, so we will not discuss optimization techniques for distributed, NUMA, and heterogeneous systems. Offloading computations to accelerators (GPU, FPGA, etc.) using solutions like OpenCL and openMP is not discussed in this book. 

This book centers around Intel x86 CPU architecture and does not provide specific tuning recipes for AMD, ARM, or RISC-V chips. Nonetheless, many of the principles discussed in further chapters apply well to those processors. Also, Linux is the OS of choice for this book, but again, for most of the examples in this book, it doesn't matter since the same techniques benefit applications that run on Windows and macOS operating systems.

All the code snippets in this book are written in C, C++, or x86 assembly languages, but to a large degree, ideas from this book can be applied to other languages that are compiled to native code like Rust, Go, and even Fortran. Since this book targets user-mode applications that run close to the hardware, we will not discuss managed environments, e.g., Java. 

Finally, the author assumes that readers have full control over the software that they develop, including the choice of libraries and compiler they use. Hence, this book is not about tuning purchased commercial packages, e.g., tuning SQL database queries.

