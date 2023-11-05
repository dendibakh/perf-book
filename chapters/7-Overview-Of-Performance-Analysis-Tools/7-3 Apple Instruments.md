## Apple Xcode Instruments

The most convinient way to do the initial performance analisys on MacOS is to use Instruments. It is an application performance analyzer and visualizer, that comes for free with Xcode. Instruments is built on top of the DTrace tracing framework that was ported to MacOS from Solaris. Instruments has many tools to inspect performance of an application and allows us to do most of the basic things that other profilers like Intel Vtune can do. The easiest way to get the profiler is to install Xcode from the Apple AppStore. The tool requires no configuration, once you install it you're ready to go.

In Instruments, you use specialized tools, known as instruments, to trace different aspects of your apps, processes, and devices over time. Instruments has a powerfull visualization mechanism. It collects data as it profiles, and presents the results to you in real time. You can gather different types of data and view them side by side which allows you to see patterns in the execution, correlate system events and find very subtle performance issues. 

In this chapter we will only showcase the "CPU Counters" instrument, which is the most relevant for this book. Instruments can also visualize GPU, network and disk activity, track memory allocations and releases, capture user events, such as mouse clicks, provide insights into power efficiency, and more. Read more about those use cases in the Instruments [documentation](https://help.apple.com/instruments/mac/current)[^1].

### What you can do with it: {.unlisted .unnumbered}

- access HW performance counters on Apple M1 and M2 processors
- find hotspots in a program along with call stacks
- inspect generated ARM assembly code side-by-side with the source code
- filter data for a selected interval on the timeline

### What you cannot do with it: {.unlisted .unnumbered}

[TODO]: does it has the same blind spots as Vtune and uProf?

### Example: Profiling Clang Compilation {.unlisted .unnumbered}

As we advertised, in this example we will show how to collect HW performance counters on Apple Mac mini with the M1 processor inside, macOS 13.5.1 Ventura, 16 GB RAM. We took one of the largest file in the LLVM codebase and profile its compilation using Clang C++ compiler, version 15.0. Here is the command line that we will profile:

```bash
$ clang++ -O3 -DNDEBUG -arch arm64 <other options ...> -c llvm/lib/Transforms/Vectorize/LoopVectorize.cpp
```

To begin, open Instruments and choose "CPU Counters" analysis type. (Here we need to jump ahead a little bit). It will open the main timeline view shown in Figure @fig:InstrumentsView, ready to start profiling. But before we start, let's configure the collection. Click and hold the red target icon \circled{1}, then select "Recording Options..." menu. It will display the dialog window shown in Figure @fig:InstrumentsDialog. This is where you can add HW performance monitoring events for collection.

![Xcode Instruments: CPU Counters options.](../../img/perf-tools/XcodeInstrumentsDialog.png){#fig:InstrumentsDialog width=50% }

To the best of our knowledge, Apple doesn't document online their HW performance monitoring events, but they provide a list of events with some minimal description in `/usr/share/kpep`. There are `plist` files that you can convert into json. For example, for the M1 processor, one can run:

```bash
$ plutil -convert json /usr/share/kpep/a14.plist -o a14.json
```

and then open `a14.json` using a simple text editor.

The second step is to set the profiling target. To do that, click and hold the name of an application (marked \circled{2} on Figure @fig:InstrumentsView) and choose the one you're interested in, set the arguments and environment variables if needed. Now, you're ready to start the collection, press the red target icon \circled{1}.

![Xcode Instruments: timeline and statistics panels.](../../img/perf-tools/XcodeInstrumentsView.jpg){#fig:InstrumentsView width=100% }

Instruments shows a timeline and constantly updates statistics about the running application. Once the program finishes, Instruments will display the image similar to Figure @fig:InstrumentsView. The compilation took 7.3 seconds and we can see how the volume of events changed over time. For example, branch mispredictions become more pronounced towards the end of the runtime. You can zoom in to that interval on the timeline to examine the functions involved.

The bottom panel shows numerical statistics. To inspect the hotspots similar to Intel Vtune's bottom-up view, select "Profile" in the menu \circled{3}, then click the "Call Tree" menu \circled{4} and check the "Invert Call Tree" box. This is exactly what we did on Figure @fig:InstrumentsView.

Instruments show raw counts along with the percentages of the total, which is useful if you want to calculate secondary metrics like IPC, MPKI, etc. On the right side, we have the hottest call stack for the function `llvm::FoldingSetBase::FindNodeOrInsertPos`. If you double-click on a function, you can inspect ARM assembly instructions generated for the source code.

To the best of our knowledge, there are no alternative profiling tools of similar quality available on MacOS platforms. Power users could use the `dtrace` framework itself by writing short (or long) command-line scripts, but it is beyond the scope of this book.

[^1]: Instruments documentation - [https://help.apple.com/instruments/mac/current](https://help.apple.com/instruments/mac/current)