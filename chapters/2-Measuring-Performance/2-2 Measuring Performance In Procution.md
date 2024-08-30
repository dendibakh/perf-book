

## Measuring Performance in Production

When an application runs in a shared infrastructure, e.g., in a public cloud, there usually will be workloads from other customers running on the same servers. With technologies like virtualization and containers becoming more popular, public cloud providers try to fully utilize the capacity of their servers. Unfortunately, it creates additional obstacles for measuring performance in such an environment. When your application shares resources with neighbor processes, its performance can become very unpredictable.

Analyzing production workloads by recreating a specific scenario in a lab can be quite tricky. Sometimes it's not possible to reproduce exact behavior for "in-house" performance testing. This is why cloud providers and hyperscalers provide tools to monitor performance directly on production systems. A code change that performs well in a lab environment does not necessarily always perform well in a production environment. Consult with your cloud service provider to see how you can enable performance monitoring of production instances. We provide an overview of continuous profilers in [@sec:ContinuousProfiling].

It's becoming a trend for large service providers to implement telemetry systems that monitor performance on user devices. One such example is the Netflix Icarus[^1] telemetry service, which runs on thousands of different devices spread around the world. Such a telemetry system helps Netflix understand how real users perceive Netflix's app performance. It enables Netflix engineers to analyze data collected from many devices and to find issues that otherwise would be impossible to find. This kind of data enables making better-informed decisions on where to focus optimization efforts.

One important caveat of monitoring production deployments is measurement overhead. Because any kind of monitoring affects the performance of a running service, we recommended to use lightweight profiling methods. According to [@GoogleWideProfiling]: "To conduct continuous profiling on datacenter machines serving real traffic, extremely low overhead is paramount". Usually, acceptable aggregated overhead is considered below 1%. Performance monitoring overhead can be reduced by limiting the set of profiled machines as well as capturing data samples less frequently.

[^1]: Presented at CMG 2019, [https://www.youtube.com/watch?v=4RG2DUK03_0](https://www.youtube.com/watch?v=4RG2DUK03_0).
