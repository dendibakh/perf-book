---
typora-root-url: ..\..\img
---

## What is discussed in this book?

This book is written to help developers better understand the performance of their application, learn to find inefficiencies, and eliminate them. *Why my hand-written archiver performs two times slower than the conventional one? Why did my change in the function cause two times performance drop? Customers are complaining about the slowness of my application, and I don't know where to start? Have I optimized the program to its full potential? What do I do with all that cache misses and branch mispredictions?* Hopefully, by the end of this book, you will have the answers to those questions.

Here is the outline of what this book contains:

* Chapter 2 discusses how to conduct fair performance experiments and analyze their results. It introduces the best practices of performance testing and comparing results.
* Chapters 3 and 4 provide basics of CPU microarchitecture and terminology in performance analysis; feel free to skip if you know this already. 
* Chapter 5 explores several most popular approaches for doing performance analysis. It explains how profiling techniques work and what data can be collected.
* Chapter 6 gives information about features provided by the modern CPU to support and enhance performance analysis. It shows how they work and what problems they are capable of solving.
* Chapters 7-9 contain recipes for typical performance problems. It is organized in the most convenient way to be used with Top-Down Microarchitecture Analysis (see [@sec:TMA]), which is one of the most important concepts of the book.
* Chapter 10 contains optimization topics not specifically related to any of the categories covered in the previous three chapters, still important enough to find their place in this book.
* Chapter 11 discusses techniques for analyzing multithreaded applications. It outlines some of the most important challenges of optimizing the performance of multithreaded applications and the tools that can be used to analyze it. The topic itself is quite big, so the chapter only focuses on HW-specific issues, like "False Sharing".

Examples provided in this book are primarily based on open-source software: Linux as the operating system, LLVM-based Clang compiler for C and C++ languages, and Linux `perf` as the profiling tool. The reason for such a choice is not only the popularity of mentioned technologies but also the fact that their source code is open, which allows us to better understand the underlying mechanism of how they work. This is especially useful for learning the concepts presented in this book. We will also sometimes showcase proprietary tools that are "big players" in their areas, for example, Intel® VTune™ Profiler.
