# Overview Of Performance Analysis Tools {#sec:secOverviewPerfTools}

This chapter gives a quick overview of the most popular tools available on major platforms. The choice will vary depending on which OS and CPU you're using. Some of the tools are cross-platform but majority are not, so it is important to know what tools are available to you. Those profiling tools are usually developed and maintained by the HW vendors themselves because they are the ones who know how to properly use performance monitoring features available on their CPUs. Unfortunately, this creates a situation when you need to install a specialized tool depending on which CPU you are using if you need to do an advanced performance engineering work. 

After reading the chapter, take the time to practice using tools that you may eventually use. Familiarize yourself with the interface and workflow of those tools. Profile the application that you work with on a daily basis. Even if you don't find any actionable insights, you will be much better prepared when the actual need comes.

[TODO]: For each tool describe:
- which platforms are supported (Windows, Linux). Is it free or not?
- how to configure it (links to the docs are fine).
- what you can do with it. 
- 1-2 screenshots of the most important analysis views.

Planned structure:

[TODO]:
```
- Intel Vtune [Done]
- AMD uprof [WIP]
- Apple Instruments
	How to install? How to configure? How to run from xcode?
	Screenshots: 1) hotspots (inverted call tree) 2) source code view
- Linux tools
	- KUTrace [MAYBE]
```