---
typora-root-url: ..\..\img
---

## Pipeline Slot {#sec:PipelineSlot}

A pipeline slot represents hardware resources needed to process one uop. Figure @fig:PipelineSlot demonstrates the execution pipeline of a CPU that can handle four uops every cycle. Nearly all modern x86 CPUs are made with a pipeline width of 4 (4-wide). During six consecutive cycles on the diagram, only half of the available slots were utilized. From a microarchitecture perspective, the efficiency of executing such code is only 50%.

![Pipeline diagram of a 4-wide CPU.](../../img/3/PipelineSlot.jpg){#fig:PipelineSlot width=40% }

Pipeline slot is one of the core metrics in Top-Down Microarchitecture Analysis (see [@sec:TMA]). For example, Front-End Bound and Back-End Bound metrics are expressed as a percentage of unutilized Pipeline Slots due to various reasons.
