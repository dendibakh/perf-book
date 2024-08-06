## What Is Discussed in this Book?

This book is written to help developers better understand the performance of their applications, learn to find inefficiencies, and eliminate them. 

* Why my hand-written compression algorithm performs two times slower than the conventional one? 
* Why did my change in the function cause a 2x performance drop? 
* Customers are complaining about the slowness of my application, where should I start?
* Have I optimized the program to its full potential? 
* What performance analysis tools are available on my platform? 
* What are the techniques to reduce the number of cache misses and branch mispredictions?

Hopefully, by the end of this book, you will be able to answer those questions.

The book is split into two parts: performance analysis and performance optimization. The first part (chapters 2-7) teaches you how to find performance problems, and the second part (chapters 8-13) teaches you how to fix them. Here is the outline of the book chapters:

* Chapter 1 is an introduction that you're reading right now.
* Chapter 2 discusses how to conduct fair performance experiments and analyze their results. It introduces the best practices for performance testing and comparing results.
* Chapter 3 provides the basics of CPU microarchitecture. You will see how theoretical ideas find their implementation by taking a closer look at Intel's Goldencove microarchitecture. 
* Chapter 4 covers terminology and metrics used in performance analysis. At the end of the chapter, we present a case study that features various performance metrics collected on four real-world applications.
* Chapter 5 explores the most popular performance analysis approaches. We describe how profiling tools work and what sort of data you can collect by using them.
* Chapter 6 examines features provided by modern Intel, AMD, and ARM-based CPUs to support and enhance performance analysis. It shows how they work and what problems they help to solve.
* Chapter 7 gives an overview of the most popular tools available on major platforms, including Linux, Windows and MacOS, running on x86- and ARM-based processors.
* Chapter 8 is about optimizing memory accesses, cache-friendly code, data structure reorganization, and other techniques.
* Chapter 9 is about optimizing computations; it explores data dependencies, function inlining, loop optimizations, and vectorization.
* Chapter 10 is about branchless programming, which is used to avoid branch misprediction.
* Chapter 11 is about machine code layout optimizations, such as basic block placement, function splitting, profile-guided optimizations and others.
* Chapter 12 contains optimization topics not specifically related to any of the categories covered in the previous four chapters, but are still important enough to find their place in this book. In this chapter, we will discuss CPU-specific optimizations, examine several microarchitecture-related performance problems, explore techniques used for optimizing low-latency applications, and give you advice on tuning your system for the best performance.
* Chapter 13 discusses techniques for analyzing multithreaded applications. It digs into some of the most important challenges of optimizing the performance of multithreaded applications. We provide a case study of five real-world multithreaded applications, where we explain why their performance doesn't scale with the increasing number of CPU threads. We also discuss cache coherency issues, such as "False Sharing" and a few tools that are designed to analyze multithreaded applications.

Examples provided in this book are primarily based on open-source software: Linux as the operating system, the LLVM-based Clang compiler for C and C++ languages, and various open-source applications and benchmarks[^1] that you can build and run. The reason is not only the popularity of the projects but also the fact that their source code is open, which enables us to better understand the underlying mechanism of how they work. This is especially useful for learning the concepts presented in this book. This doesn't mean that we will never showcase proprietary tools. For example, we extensively use Intel® VTune™ Profiler.

[TODO]: mention that in this book x86 == x86-64
[TODO]: spell out SW = software, and HW = hardware

Prior compiler experience helps a lot in performance-related work. Sometimes it's possible to obtain attractive speedups by forcing the compiler to generate desired machine code through various hints. You will find many such examples throughout the book. Luckily, most of the time, you don't have to be a compiler expert to drive performance improvements in your application. The majority of optimizations can be done at a source code level without the need to dig down into compiler sources. 

[^1]: Some people don't like when their application is called a "benchmark". They think that benchmarks are something that is synthesized, and contrived, and does a poor job of representing real-world scenarios. In this book, we use the terms "benchmark", "workload", and "application" interchangeably and don't mean to offend anyone.