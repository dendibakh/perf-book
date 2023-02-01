# Overview Of Performance Analysis Tools {#sec:secOverviewPerfTools}

In this section we cover architecture-specific tools first, then OS-specific tools.

[TODO]: For each tool describe:
- which platforms are supported (Windows, Linux). Is it free or not?
- how to configure it (links to the docs are fine).
- what you can do with it. 
- 1-2 screenshots of the most important analysis views.

Planned structure:

```
- Intel Vtune
	Recapture screenshots: 1) hotspots view, 2) source code view, 3) microarchitectural exploration, 4) platform view.
	Also, briefly describe the memory access and threading analysis types.
	Show usage of marker APIs

- AMD uprof
    WIP
	
- Apple Instruments
	How to install
	How to configure
	Run from xcode?
	Screenshots: 1) hotspots (inverted call tree) 2) source code view

- Linux tools

	- Linux perf
		Many examples throghout the book. Write a general information here.
	- Flamegraphs
		Migrate from previous chapters
	- KDAB hotspots
		
	- Netflix FlameScope
	
	- KUTrace

- Windows tools

	- Windows ETW
        WIP
    - Tracy, Optick, Superluminal
        WIP
```