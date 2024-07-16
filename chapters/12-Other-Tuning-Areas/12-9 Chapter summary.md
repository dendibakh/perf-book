## Chapter Summary {.unlisted .unnumbered}

* Processors from different vendors are not created equal. They differ in terms of instruction set architecture (ISA) that they support and microarchitecture implementation. Reaching peak performance often requires leveraging the latest ISA extensions and tuning the application for a specific CPU microarchitecture.
* CPU dispatching is a technique that enables you to introduce platform-specific optimizations. Using it, you can provide a fast path for a specific microarchitecture while keeping a generic implementation for other platforms.
* We explored several performance corner cases that are caused by the interaction of the application with the CPU microarchitecture. These include memory ordering violations, misaligned memory accesses, cache aliasing, and denormal floating-point numbers.
* We also discussed a few low-latency tuning techniques that are essential for applications that require fast response times. We showed how to avoid page faults, cache misses, TLB shootdowns, and core throttling on a critical path.
* System tuning is the last piece of the puzzle. Some knobs and settings may affect the performance of your application. It is crucial to ensure that the system firmware, the OS, or the kernel does not destroy all the efforts put into tuning the application. 

\sectionbreak



