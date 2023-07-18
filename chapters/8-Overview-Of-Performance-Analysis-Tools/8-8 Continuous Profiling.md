## Continuous Profiling

In Chapter 6, we covered the various approaches available for conducting a performance analysis, including but not limited to instrumentation, tracing, and sampling. Among these three approaches, sampling imposes relatively minor runtime overhead and requires the least amount of upfront work while still offering valuable insight into application hotspots. But this insight is limited to the specific point in time when the samples are gathered – what if we could add a time dimension to this sampling? Instead of knowing that FunctionA consumes 30% of CPU cycles at one particular point in time, what if we could track changes in FunctionA’s CPU usage over days, weeks, or months? Or detect changes in its stack trace over that same
timespan, all in production? Continuous Profiling emerged to turn these ideas into reality.

Continuous Profiling is exactly what it sounds like – a systemwide, sample-based profiler that is always on, albeit at a low sample rate to minimize runtime impact. Google introduced the concept in the 2010 paper “Google-Wide Profiling: A Continuous Profiling Infrastructure for Data Centers”, which championed the value of always-on profiling in production environments. However, it took nearly a decade before it gained traction in the industry:

1. In March 2019, Google Cloud released its Continuous Profiler for GA.
2. In July 2020, AWS released CodeGuru Profiler for GA
3. In August 2020, Datadog released its Continuous Profiler for GA
4. In December 2020, New Relic acquired the Pixie Continuous Profiler
5. In Jan 2021, Pyroscope released its opensource Continuous Profiler
6. In October 2021, Elastic acquired Optimize and its Continuous Profiler (Prodfiler) and Polar
Signals released its opensource Parca Continuous Profiler
7. In December 2021, Splunk releases its AlwaysOn Profiler
8. In March 2022, Intel acquired Granulate and its Continuous Profiler (gProfiler)

And new entrants into this space continue to pop up in both opensource and commercial varieties. Some of these offerings require more hand-holding than others. For example, some require source code or configuration file changes to begin profiling. Others require different agents for different language runtimes (e.g., ruby, python, golang, C/C++/Rust). The best of them have crafted secret sauce around eBPF so that nothing other than simply installing the runtime agent is necessary.

They also differ in the number of language runtimes supported, the work required for obtaining debug symbols for readable stack traces, and the type of system resources that can be profiled aside from CPU (e.g., memory, I/O, locking, etc.). While Continuous Profilers differ in the aforementioned aspects, they all share the common function of providing low-overhead, sample-based profiling for various language runtimes, along with remote stack trace storage for web-based search and query capability.

Where is Continuous Profiling headed? Thomas Dullien, co-founder of Optimyze which developed the innovative Continuous Profiler Prodfiler, delivered the Keynote at QCon London 2023 in which he expressed his wish for a cluster-wide tool that could answer the questions, “Why is this request slow?” or “Why is this request expensive?” In other words, he wishes for a Continuous Profiler that can not only highlight resource-intensive portions of an application, but can also pinpoint the root cause of overall application latency or throughput issues. Those of us who have ever profiled multithreaded applications are well aware that functions with the highest CPU usage are seldom the application bottleneck.

Thankfully, a new generation of Continuous Profilers has emerged that employ AI with LLM-inspired architectures to process profile samples, analyze the relationships between functions, and finally pinpoint with high accuracy the functions and libraries which directly impact overall throughput and latency. One such company that offers this today is Raven.io. And as competition intensifies in this space, innovative capabilities will continue to grow so that datacenter-wide performance analysis becomes as powerful and robust as that of a single machine.