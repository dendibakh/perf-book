---
typora-root-url: ..\..\img
---

## What Is Discussed in this Book?

This book is written to help developers better understand the performance of their application, learn to find inefficiencies, and eliminate them. *Why my hand-written compression algorithm performs two times slower than the conventional one? Why did my change in the function cause performance to drop by half? Customers are complaining about the slowness of my application, where should I start? Have I optimized the program to its full potential? What performance analysis tools are available on my platform? What are the techniques to reduce the number of cache misses and branch mispredictions?* Hopefully, by the end of this book, you will have the answers to those questions.

Here is the outline of what this book contains:

[TODO]: update below

* Chapter 2 discusses how to conduct fair performance experiments and analyze their results. It introduces the best practices for performance testing and comparing results.
* Chapters 3 provides basics of CPU microarchitecture and Chapter 4 covers terminology and metrics used in performance analysis; we recommend you not to skip these chapters even if you think you know this already. 
* Chapter 5 explores several of the most popular approaches for doing performance analysis. It explains how profiling techniques work, what runtime data can be collected, and how it can be done.
* Chapter 6 examines features provided by modern CPUs to support and enhance performance analysis. It shows how they work and what problems they can solve.
* Chapter 7 gives an overview of the most popular tools available on major platforms, including Linux, Windows and MacOS, running on x86- and ARM-based processors.
* Chapters 8-11 contain recipes for typical performance problems. These chapters are organized according to the Top-down Microarchitecture Analysis methodology, which is one of the most important concepts of the book. Don't worry if some terms are not yet clear to you, we will cover everything step by step. Chapter 8 (Memory Bound) is about optimizing memory accesses, cache friendly code, memory profiling, huge pages, and a few other techniques. Chapter 9 (Core Bound) is about optimizing computations and explores function inlining, loop optimizations, and vectorization. Chapter 10 (Bad Specualtion) is about branchless programming that is used to avoid frequently mispredicted branches. Chapter 11 (FrontEnd Bound) is about machine code layout optimizations, such as basic block placement, function splitting, profile-guided optimizations and others.
* Chapter 13 contains optimization topics not specifically related to any of the categories covered in the previous four chapters, but are still important enough to find their place in this book. There you will find low-latency techniques, tips on tuning your system for the best performance, faster alternatives to standard library funcitons, and others.
* Chapter 14 discusses techniques for analyzing multithreaded applications. It outlines some of the most important challenges of optimizing the performance of multithreaded applications and the tools that can be used to analyze them. The topic itself is quite big, so the chapter only focuses on HW-specific issues, like "False Sharing".
* Chapter 15 talks about the current and future trends in the world of SW and HW performance. We discuss advances in traditional design of computer systems as well as some innovative ideas.

Examples provided in this book are primarily based on open-source software: Linux as the operating system, the LLVM-based Clang compiler for C and C++ languages, and Linux `perf` as the profiling tool. The reason for such a choice is not only the popularity of the mentioned technologies but also the fact that their source code is open, which allows us to better understand the underlying mechanism of how they work. This is especially useful for learning the concepts presented in this book. We will also sometimes showcase proprietary tools that are "big players" in their areas, for example, Intel® VTune™ Profiler.
