# Overview Of Performance Analysis Tools {#sec:secOverviewPerfTools}

In this section we cover architecture-specific tools first, then OS-specific tools.

[TODO]: For each tool describe:
- which platforms are supported (Windows, Linux). Is it free or not?
- how to configure it (links to the docs are fine).
- what you can do with it. 
- 1-2 screenshots of the most important analysis views.

Planned structure:

```
- Intel Vtune [Done]
- AMD uprof [WIP]
- Apple Instruments
	How to install? How to configure? How to run from xcode?
	Screenshots: 1) hotspots (inverted call tree) 2) source code view
- Linux tools
	- Linux perf, mention KDAB hotspots [Many examples throghout the book. Write a general information here]
	- Flamegraphs [Migrate from previous chapters]
	- Netflix FlameScope [TODO]
	- KUTrace [TODO]
- Windows tools
	- Windows ETW [WIP]
- Specialized profilers
	- Tracy, Optick, Superluminal [WIP]
```