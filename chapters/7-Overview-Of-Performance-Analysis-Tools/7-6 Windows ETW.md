## Event Tracing for Windows {#sec:ETW}

Microsoft has developed a system-wide tracing facility named Event Tracing for Windows (ETW). It was originally intended for helping device driver developers, but later found use in analyzing general-purpose applications as well. ETW is available on all supported Windows platforms (x86 and ARM) with the corresponding platform-dependent installation packages. ETW records structured events in user and kernel code with full call stack trace support, which enables you to observe software dynamics in a running system and solve many challenging performance issues.

### How to configure it {.unlisted .unnumbered}

Recording ETW data is possible without any extra download since Windows 10 with `WPR.exe`. But to enable system-wide profiling you must be an administrator and have the `SeSystemProfilePrivilege` enabled. The \underline{W}indows \underline{P}erformance \underline{R}ecorder tool supports a set of built-in recording profiles that are suitable for common performance issues. You can tailor your recording needs by authoring a custom performance recorder profile xml file with the `.wprp` extension.

If you want to not only record but also view the recorded ETW data you need to install the Windows Performance Toolkit (WPT). You can download it from the Windows SDK[^1] or ADK[^2] download page. The Windows SDK is huge; you don't necessarily need all its parts. In our case, we just enabled the checkbox of the Windows Performance Toolkit. You are allowed to redistribute WPT as a part of your own application.

### What you can do with it: {.unlisted .unnumbered}

- Identify hotspots with a configurable CPU sampling rate from 125 microseconds up to 10 seconds. The default is 1 millisecond which costs approximately 5--10% runtime overhead.
- Determine what blocks a certain thread and for how long (e.g., late event signals, unnecessary thread sleep, etc).
- Examine how fast a disk serves read/write requests and discover what initiates that work.
- Check file access performance and patterns (including cached read/writes that lead to no disk IO).
- Trace the TCP/IP stack to see how packets flow between network interfaces and computers.

All the items listed above are recorded system-wide for all processes with configurable call stack traces (kernel and user mode call stacks are combined). It's also possible to add your own ETW provider to correlate the system-wide traces with your application behavior. You can extend the amount of data collected by instrumenting your code. For example, you can inject enter/leave ETW tracing hooks in functions into your source code to measure how often a certain function was executed.

### What you cannot do with it: {.unlisted .unnumbered}

ETW traces are not useful for examining CPU microarchitectural bottlenecks. For that, use vendor-specific tools like Intel VTune, AMD uProf, Apple Instruments, etc.

ETW traces capture the dynamics of all processes at the system level, however, it may generate a lot of data. For example, capturing thread context switching data to observe various waits and delays can easily generate 1--2 GB per minute. That's why it is not practical to record high-volume events for hours without overwriting previously stored traces.

If you'd like to learn more about ETW, there is a more detailed discussion in Appendix D. We explore tools to record and analyze ETW and present a case study of debugging a slow start of a program.

[^1]: Windows SDK Downloads - [https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
[^2]: Windows ADK Downloads - [https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads](https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads)
