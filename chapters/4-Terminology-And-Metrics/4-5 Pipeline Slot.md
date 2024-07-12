---
typora-root-url: ..\..\img
---

## Pipeline Slot {#sec:PipelineSlot}

Another important metric which some performance tools use is the concept of a *pipeline slot*. A pipeline slot represents the hardware resources needed to process one $\mu$op. Figure @fig:PipelineSlot demonstrates the execution pipeline of a CPU that has 4 allocation slots every cycle. That means that the core can assign execution resources (renamed source and destination registers, execution port, ROB entries, etc.) to 4 new $\mu$ops every cycle. Such a processor is usually called a *4-wide machine*. During six consecutive cycles on the diagram, only half of the available slots were utilized. From a microarchitecture perspective, the efficiency of executing such code is only 50%.

![Pipeline diagram of a 4-wide CPU.](../../img/terms-and-metrics/PipelineSlot.jpg){#fig:PipelineSlot width=40% }

[TODO]: update. Apple published that M1 has 8-wide allocation and M3 is 9-wide, see Table 4.10. μop Execution Bandwidth.

Intel's Skylake and AMD Zen3 cores have 4-wide allocation. Intel's SunnyCove microarchitecture was a 5-wide design. As of 2023, most recent Goldencove and Zen4 architectures both have 6-wide allocation. Apple M1 design is not officially disclosed but is measured to be 8-wide.[^1]

Pipeline slot is one of the core metrics in Top-down Microarchitecture Analysis (see [@sec:TMA]). For example, Front-End Bound and Back-End Bound metrics are expressed as a percentage of unutilized Pipeline Slots due to various bottlenecks.

[^1]: Apple Microarchitecture Research - [https://dougallj.github.io/applecpu/firestorm.html](https://dougallj.github.io/applecpu/firestorm.html)