---
typora-root-url: ..\..\img
---

## Code Instrumentation {#sec:secInstrumentation}

Probably the first approach for doing performance analysis ever invented is code *instrumentation*. It is a technique that inserts extra code into a program to collect specific runtime information. [@lst:CodeInstrumentation] shows the simplest example of inserting `printf` statements at the beginning of the function to count the number of times this function was called. After that you run the program and count the number of times you see "foo is called" in the output. I think every programmer in the world did it at some point of their carreer at least once.

Listing: Code Instrumentation

~~~~ {#lst:CodeInstrumentation .cpp}
int foo(int x) {
+ printf("foo is called");
  // function body...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A slightly more interesting example of code instrumentation is presented in [@lst:CodeInstrumentationHistogram]. The plus sign at the beginning of a line means that this line was added and is not present in the original code. In general, instrumentation code is not meant to be pushed into the codebase, it's rather for collecting the needed data and then can be thrown away. I usually just copy-paste a version of this code into whatever project I'm working on and then delete it. It is simple enough and can be adjusted to your specific needs quickly. 

In this made-up code example, the function `findObject` searches the coordinates of an object with some properties `p` on a map. The function `findObj` returns the confidence level that we located the right object with the current coordinates `c`. If it is an exact match, we stop the search loop and return the coordinates. If the confidence is above the `threshold`, we choose to `zoomIn` to find more precise location of the object. Otherwise, we get the new coordinates within the `searchRadius` to try our search next time.



Listing: Code Instrumentation

~~~~ {#lst:CodeInstrumentationHistogram .cpp}
+ struct histogram {
+   std::map<uint32_t, std::map<uint32_t, uint64_t>> hist;
+   ~histogram() {
+     for (auto& tripCount : hist)
+       for (auto& updateCount : tripCount.second)
+         std::cout << "[" << tripCount.first << "][" 
+                   << updateCount.first << "] : " 
+                   << updateCount.second << "\n";
+   }
+ };
+ histogram h;

+ struct incrementor {
+   uint32_t loopTripCount = 0;
+   uint32_t updateCount = 0;
+   ~incrementor() {
+ 	   h.hist[loopTripCount][updateCount]++;
+   }
+ };

Coords findObject(Coords c, ObjParams p, float searchRadius) {
+ incrementor inc;
  while (true) {
+   inc.tripCount++;  
    float match = findObj(c, p);
    if (exactMatch(match))
      return c;   
    if (match > threshold) {
      searchRadius = zoomIn(c, searchRadius);
+     inc.updateCount++;
    }
    c = getNewCoords(searchRadius);
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method provides very detailed information when you need specific knowledge about the execution of the program. Code instrumentation allows us to track any information about every variable in the program.

Instrumentation based profiling methods are mostly used on a macro level, not on the micro(low) level. Using such a method often yields the best insight when optimizing big pieces of code because you can use a top-down approach (instrumenting the main function then drilling down to its callees) of locating performance issues. While code instrumentation is not very helpful in the case of small programs, it gives the most value and insight by letting developers observe the architecture and flow of an application. This technique is especially helpful for someone working with an unfamiliar codebase.

It's also worth mentioning that code instrumentation shines in complex systems with many different components that react differently based on inputs or over time. Sampling techniques (discussed in [@sec:profiling]) squash that valuable information, not allowing us to detect abnormal behaviors. For example, in games, usually, there is a renderer thread, physics thread, animations thread, etc. Instrumenting such big modules help to reasonably quickly to understand what module is the source of issues. As sometimes, optimizing is not only a matter of optimizing code but also data. For example, rendering is too slow because of uncompressed mesh, or physics are too slow because of too many objects in the scene.

The technique is heavily used in real-time scenarios, such as video games and embedded development. Many profilers[^3] mix up instrumentation with other techniques discussed in this chapter (tracing, sampling).

While code instrumentation is powerful in many cases, it does not provide any information about how the code executes from the OS or CPU perspective. For example, it can't give you information about how often the process was scheduled in and out from the execution (known by the OS) or how much branch mispredictions occurred (known by the CPU). Instrumented code is a part of an application and has the same privileges as the application itself. It runs in userspace and doesn't have access to the kernel.

But more importantly, the downside of this technique is that every time something new needs to be instrumented, say another variable, recompilation is required. This can become a burden to an engineer and increase analysis time. It is not all downsides, unfortunately. Since usually, you care about hot paths in the application, you're instrumenting the things that reside in the performance-critical part of the code. Inserting instrumentation code in a hot piece of code might easily result in a 2x slowdown of the overall benchmark[^2]. Finally, by instrumenting the code, you change the behavior of the program, so you might not see the same effects you saw earlier.

All of the above increases time between experiments and consumes more development time, which is why engineers don't manually instrument their code very often these days. However, automated code instrumentation is still widely used by compilers. Compilers are capable of automatically instrumenting the whole program and collect interesting statistics about the execution. The most widely known use cases are code coverage analysis and Profile Guided Optimizations (see [@sec:secPGO]).

When talking about instrumentation, it's important to mention binary instrumentation techniques. The idea behind binary instrumentation is similar but done on an already built executable file as opposed to on a source code level. There are two types of binary instrumentation: static (done ahead of time) and dynamic (instrumentation code inserted on-demand as a program executes). The main advantage of dynamic binary instrumentation is that it does not require program recompilation and relinking. Also, with dynamic instrumentation, one can limit the amount of instrumentation to only interesting code regions, not the whole program.

Binary instrumentation is very useful in performance analysis and debugging. One of the most popular tools for binary instrumentation is Intel [Pin](https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool)[^1] tool. Pin intercepts the execution of the program in the occurrence of an interesting event and generates new instrumented code starting at this point in the program. It allows collecting various runtime information, for example: 

* instruction count and function call counts. 
* intercepting function calls and execution of any instruction in an application.
* allows "record and replay" the program region by capturing the memory and HW registers state at the beginning of the region.

Like code instrumentation, binary instrumentation only allows instrumenting user-level code and can be very slow.

[^1]: PIN - [https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool](https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool)
[^2]: Remember not to benchmark instrumented code, i.e., do not measure score and do analysis in the same run.
[^3]: A few examples: optick ([https://optick.dev](https://optick.dev)), tracy ([https://bitbucket.org/wolfpld/tracy](https://bitbucket.org/wolfpld/tracy)), superluminal ([https://superluminal.eu](https://superluminal.eu)).

