---
typora-root-url: ..\..\img
---

[TODO]: discuss scheduling issues (separate section)

# Optimizing Multithreaded Applications {#sec:secOptMTApps}

Modern CPUs are getting more and more cores each year. As of 2020, you can buy an x86 server processor which will have more than 50 cores! And even a mid-range desktop with 8 execution threads is a pretty usual setup. Since there is so much processing power in every CPU, the challenge is how to utilize all the HW threads efficiently. Preparing software to scale well with a growing amount of CPU cores is very important for the future success of the application.

Multithreaded applications have their own specifics. Certain assumptions of single-threaded execution get invalidated when we're dealing with multiple threads. For example, we can no longer identify hotspots by looking at a single thread since each thread might have its own hotspot. In a popular [producer-consumer](https://en.wikipedia.org/wiki/Producer–consumer_problem)[^5] design, the producer thread may sleep during most of the time. Profiling such a thread won't shed light on the reason why our multithreaded application is not scaling well.

[TODO]: Talk about two types of applications:
- massively parallel
- require synchronization

[TODO]: Preview what we will talk about: first explore massively parallel, then explore how to find expensive locks.

[^5]: Producer-consumer pattern - [https://en.wikipedia.org/wiki/Producer-consumer_problem](https://en.wikipedia.org/wiki/Producer-consumer_problem)
