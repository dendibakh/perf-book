## Event Tracing for Windows

Microsoft has invested in a system wide tracing facility named Event Tracing for Windows (ETW). The main difference to the many Linux tracers is its ability to write structured events in user and kernel code with full stack trace support. Stack traces are essential to solve many challenging performance issues. They are the difference between knowing that someone did consume all CPU/Disk/Network/... vs. who did it in which source file. ETW is available on all supported Windows platforms (x86, x64 and ARM) with the corresponding platform dependent installation packages.
 
### What can you do with it: {.unlisted .unnumbered}

- Everything below is recorded system wide for all processes with configurable stack traces (kernel and user mode stacks combined).
- Look at CPU hotspots with a configurable CPU sampling rate from 1/8 ms = 8 kHz up to 10 s = 1/10 Hz. Default is 1ms which costs ca. 5-10% execution performance.
- Who blocks your threads and for how long (e.g. late event signals, unnecessary thread sleeps, ...) with Context Switch traces.
- Find system issues where you need to track multi process causality chains or even cross machine with the help of correlation events to sync timepoints.
- Examine how fast your disk/s serves read/write requests and who initiates that work.
- Check file access performance and patterns (includes cached read/writes which lead to no disk IO).
- Trace the TCP/IP stack how packets flow between network interfaces and computers.
- Add your own ETW Trace provider to correlate the system wide traces with your application behavior.

### What you cannot do with it: {.unlisted .unnumbered}

- Examine CPU bottlenecks in detail. Use VTune which offers much more details how the CPU accesses code and data.
- How often a method was executed. If you instrument your own methods with enter/leave ETW tracing it is possible.
- Record high volume events for hours like thread wait (Context Switch) tracing. ETW records at system level all processes which is great, but generates a lot (ca. 1-2 GB/minute) of data.

### Getting ETW Data

To enable system wide profiling you must be administrator and have the privilege *SeSystemProfilePrivilege* enabled. 

Recording ETW data is possible without any extra download since Windows 10 with Wpr.exe. The \underline{W}indows \underline{P}erformance \underline{R}ecorder tool supports a set of built-in recording profiles which are ok for common performance issues. You can tailor your recording needs by authoring a custom performance recorder profile xml file with the `.wprp` extension.

If you are running Windows 10 or you want not only record but also view the recorded ETW data you need to install the Windows Performance Toolkit.
You can download the Windows Performance Toolkit from the Windows SDK[^1] or ADK[^2] download page. The installation is a two step process. First you download a small installer which you start. There you can select in the SDK Installer UI just the parts of the huge Windows SDK you need. In our case we just enable the checkbox of the Windows Performance Toolkit and install it. You are allowed to redistribute WPT e.g. as part of your own application.

### ETW Recording Tools {.unlisted .unnumbered}

- wpr.exe: a command line recording tool, part of Windows 10 and Windows Performance Toolkit.
- WPRUI.exe: a simple UI for recording ETW data, part of Windows Performance Toolkit
- xperf: a command line predecessor of wpr, part of Windows Performance Toolkit.
- PerfView[^3]: a graphical recording and analysis tool with the main focus on .NET Applications. Open-source by Microsoft.
- Performance HUD[^7]: a little known but very powerful GUI tool to track UI delays, User/Handle leaks via live ETW recording all unbalanced resource allocations with a live display of leaking/blocking stack traces.
- ETWController[^4]: a recording tool with the ability to record keyboard input and screenshots along with ETW data. Supports also distributed profiling on two machines simultaneously. Open-sourced by Alois Kraus.
- UIForETW[^6]: a wrapper around xperf with special options to record data for Google Chrome issues. Can also record keyboard and mouse input. Open-sourced by Bruce Dawson.
  
### ETW Viewing/Analysis Tools {.unlisted .unnumbered}

- Windows Performance Analyzer (WPA): the most powerful UI for viewing ETW data.  WPA can visualize and overlay Disk, CPU, GPU, Network, Memory, Process and many more data sources to get a holistic understanding how your system behaves and what it was doing. Although the UI is very powerful it may also be quite complex for beginners.  WPA supports plugins to process any data, not just ETW traces. Today you can view Linux/Android[^8] profiling data with WPA generated from tools like Linux perf, LTTNG, Perfetto and the following log file formats: dmesg, Cloud-Init, WaLinuxAgent, AndoidLogcat.

- ETWAnalyzer[^5]: reads ETW data and generates aggregate summary Json files which can be queried, filtered and sorted at command line or exported to a CSV file.

- PerfView: mainly used to troubleshoot .NET applications. The ETW events fired for Garbage Collection and JIT compilation are parsed and easily accessible as reports or CSV data. 

Next, we will take a look at the example of using ETWController to capture ETW traces and WPA to visualize them.

### Case Study - Slow Program Start {.unlisted .unnumbered}

**Problem statement:** When double clicking on a downloaded executable in Windows Explorer it is started with a noticeable delay. Something seems to delay process start.

#### Setup {.unlisted .unnumbered}

- Download a tool to record ETW data and screenshots like ETWController[^4].
- Download the latest Windows 11 Performance Toolkit[^1] to be able to view the data with WPA. 
  - Ensure that the newer Win 11 wpr.exe comes first in your path by moving the install folder of the WPT before the C:\\Windows\\system32 in the System Environment dialog. This is how it should look like: 

```
    C>where wpr 
    C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit\wpr.exe
    C:\Windows\System32\wpr.exe
```

#### Capture traces {.unlisted .unnumbered}

- Start ETWController
- Select the CSwitch profile to track thread wait times along with the other default recording settings. Keep the check boxes *"Record mouse clicks"* and *"Take cyclic screenshots"* enabled to be later able to navigate to the slow spots with the help of the screen shots. See @fig:ETWControllerUI.
 - Press *"Start Recording"*
 - Download some executable from the internet, unpack it and double click the executable to start it. 
 - After that you can stop profiling by pressing the *"Stop Recording"* button. 

![ETWController UI screenshot.](../../img/perf-tools/ETWController.png){#fig:ETWControllerUI width=80%}

Stopping profiling the first time takes a bit longer because for all managed code synthetic pdbs are generated which is a one time operation. After profiling has reached the Stopped state you can press the *"Open in WPA"* button to load the ETL file into the Windows Performance Analyzer with an ETWController supplied profile. The CSwitch profile generates a large amount of data which is stored in a 4 GB ring buffer which allows you to record 1-2 minutes before the oldest events are overwritten. Sometimes it is a bit of an art to stop profiling at the right time point. If you have sporadic issues you can keep recording enabled for hours and stop it when an event like a log entry in a file shows up, which is checked by a polling script, to stop profiling when the issue has occurred.

![Screenshot captured with ETWController viewed in Browser.](../../img/perf-tools/ETWController_Screenshot.png){#fig:ETWControllerScreenshot width=80% }

Windows supports Event Log and Performance Counter triggers which allow one to start a script when a performance counter reaches a threshold value or a specific event is written to an event log. If you need more sophisticated stop triggers you should take a look at PerfView which allows one to define a Performance Counter threshold which must be reached and stay there for x seconds before profiling is stopped. This way random spikes are no longer triggering false positives. 

#### Analysis in WPA {.unlisted .unnumbered}

![WPA overview of the trace showing a process start blocked by defender activity.](../../img/perf-tools/WPA_SlowProcessStart_DefenderOverhead.png){#fig:DefenderOverhead width=100% }

WPA supports custom profiles to configure the graph and table data for visualizing CPU, disk, files, etc. in the way you like best. Originally it was developed for device driver developers which is reflected by the built-in profiles which do not focus on application development. ETWController brings its own profile (*Overview.wpaprofile*) which you can set as default profile under *Profiles - Save Startup Profile* to always use the performance overview profile.

On the screenshot @fig:DefenderOverhead, the view is divided into two parts: *CPU Usage (Sampled)* and *CPU Usage (Precise)*, let's understand the difference. The upper half shows sampled graph which is useful to see where CPU is spent, similar to hotspots view in other profiling tools. The lower half shows precise graph, which takes into account time intervals during a process was not running (wall time). Such data is generated by the Windows Thread Scheduler handling context switch events which provides data, e.g. how long and on which CPU a thread was running (CPU Usage), how long it was blocked in a kernel call (Wait), in which priority and how long the thread had been waiting for a CPU to become free (Ready Time), etc.

The methods in the *CPU Usage (Precise)* graph with highest CPU are most likely not the actual CPU consumers. A Context switch event is (simplified!) generated when a thread hits a blocking OS call like `WaitForSingleObject` or `WaitForMultipleObjects`. If a thread is e.g. in a busy for loop spinning billions of iterations but later taking a lock all CPU will be attributed to the lock call which calls into a blocking OS call. Only the blocking operation generates a Context Switch event and not high CPU. Although the CPU consumption of a thread is measured exactly it will not help you to locate busy CPU consumers. To find CPU bottlenecks you need to look into CPU sampling data. If you want to know why your thread was not running then you need Context Switch traces. What most users expect would be a combined view which show wait times and CPU hotspots in one tool, but this is so far not supported in WPA. ETWAnalyzer merges the data, but it is a console only application with no UI.

We can examine the screenshots taken by ETWController to find where slowness was observed. An example is shown in figure @fig:ETWControllerScreenshot. When the profiling data is saved (the file named xx.etl) another folder named *xx.etl.Screenshots* is created. This contains all screenshots and a *Report.html* file which you can view in the browser. Every recorded keyboard/mouse interaction gets a screenshot of the form Screenshot_EventNumber e.g. Screenhot_63.jpg. This is the screenshot file of the double click event where the process start was delayed. The mouse pointer position is marked as a green square, except if a click event did occur, then it is red. This makes it easy to spot when and where a mouse click was performed.

The slow click event number 63 we can locate in the profiling data in the WPA Overview view. Then you can zoom in to the interesting time region of a potentially longer recording. The event number is part of the *Generic Events HookTracer Events(Slow, Mouse, Keyboard)* WPA view which visualizes all keyboard, mouse and timer based screenshots. 


See figure @fig:DefenderOverhead. When you double click in explorer to start an executable you would first check if a delay in explorer.exe is happening. Since we are dealing with delays it makes sense to look at the *CPU Usage (Precise) Waits* Graph. There you will find after the first column after process *New Thread Stack (Stack Tag)* which shows the summary of all threads and what they were doing. If we look deeper we find *Antivirus - Windows Defender* with a delay of 1.068s which can be visualized as bar chart to nicely display correlations across processes.

You might be familiar with stack traces, but not necessarily stack tags. When you read a call stack you try to understand what an application was doing and mentally map the call stack to the applications intent. Lets suppose a deep stack trace which consumes a lot of CPU 

----------------------------------------------------------------------------------------------------
Stack Tag                   Stack                                           CPU ms             Wait ms
---------                   ----------------------------------------        ---------------    ----------
Windows Defender            YourApp.exe!main()                              5000               10000

                            YourApp.exe!logic1()                            3000               5000  

                             YourApp.exe!logic2()                            2000               3000

                             YourApp.exe!logic3()                            2000               3000

                             YourApp.exe!logic4()                            2000               3000

                              YourApp.exe!logic5()                            1000               2500

                                YourApp.exe!logic6()                            500                2300

                                YourApp.exe!readfile()                          500                2300

                                  KernelBase.dll!CreateFileInternal               396              2200

                                  apphelp.dll!InsHook_NtCreateFile                396              2200

                                  ntdll.dll!NtCreateFile                          396              2200

                                  ...                                             396              2200

                                  FLTMGR.SYS!FltpCreate                           396              2200

                                  FLTMGR.SYS!FltpPassThroughInternal              396              2200

                                  FLTMGR.SYS!FltpPerformPreCallbacksWorker        396              2200

                                  WdFilter.sys!<PDB not found>                    396              2200

                                  ...                                             ...               ...

----------------------------------------------------------------------------------------------------
Table: Stacktag Example. {#tbl:stacktag_example}

At a high level you know that logic1 is running which many layers below tries to read from a file where the file open operation (CreateFile) is delayed for 2500ms. If only user mode stacks are present you must assume that the file system was just slow. But with ETW see also what the kernel is doing. In this case CreateFile is intercepted by Windows Defender (WdFilter.sys = Windows Defender Filter Driver) for which Microsoft does not deliver symbol information. We know that our call was delayed by Antivirus. To check where else the Antivirus Scanner is interfering with your application you need to unfold all stacks where WdFilter.sys is poping up, which is a time consuming operation. One would like to group the stacks which are interecepted by Defender into an extra bucket. That is what stack tags are meant for: To give a key method of a stack trace a descriptive name. Stacktags are method and module pattern expressions in an external XML file (in WPA: Trace -Trace Properties-Stack Tags Definitions) which are defined like this:
```
  <Tag Name="Windows Defender" Priority="1">
    <Entrypoint Module="WdFilter.sys" Method="*"/>
    <Entrypoint Module="mssecflt.sys" Method="*"/>
  </Tag>
```
Stack tag matching works from bottom to top where the first matching stack tag definition wins. That behavior has the nice property that you can sum up all stacktags to get the total CPU/Wait overhead for this stacktag. Since ETW stack traces combine user and kernel stacks it is easy to estimate AV overhead by defining a stacktag for all AV device drivers which are showing up in your application stack traces in CPU Sampling and Context Switch traces because the AV drivers are intercepting your user mode calls. 

The Defender stacktag matches two Defender device drivers which intercept (mainly) CreateProcess and File related operations. If e.g. the CreateFile call is delayed by one of these drivers we can directly see how much Wait and CPU by this driver was introduced by looking at the aggregated stack tag metrics. If the tag is absent we know that no Defender was running at that point in time. 
See[^9] for a more detailed explanation how you can define your own stacktag definitions. The stacktags from the ETWController profile originate from ETWAnalyzer[^10] which is the result of hundreds of performance issues investigated over a decade in Windows, .NET, .NET Core, GPU and Antivirus device drivers. 

[^1]: Windows SDK Downloads [https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
[^2]: Windows ADK Downloads [https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads](https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads)
[^3]: PerfView [https://github.com/microsoft/perfview](https://github.com/microsoft/perfview)
[^4]: ETWController [https://github.com/alois-xx/etwcontroller](https://github.com/alois-xx/etwcontroller)
[^5]: ETWAnalyzer [https://github.com/Siemens-Healthineers/ETWAnalyzer](https://github.com/Siemens-Healthineers/ETWAnalyzer)
[^6]: UIforETW [https://github.com/google/UIforETW](https://github.com/google/UIforETW)
[^7]: Performance HUD [https://www.microsoft.com/en-us/download/100813](https://www.microsoft.com/en-us/download/100813)
[^8]: Microsoft Performance Tools Linux / Android [https://github.com/microsoft/Microsoft-Performance-Tools-Linux-Android](https://github.com/microsoft/Microsoft-Performance-Tools-Linux-Android)
[^9]: Stacktags [https://learn.microsoft.com/en-us/windows-hardware/test/wpt/stack-tags](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/stack-tags)
[^10]: ETWAnalyzer Stacktags [https://github.com/Siemens-Healthineers/ETWAnalyzer/blob/main/ETWAnalyzer/Configuration/default.stacktags](https://github.com/Siemens-Healthineers/ETWAnalyzer/blob/main/ETWAnalyzer/Configuration/default.stacktags)
