---
typora-root-url: ..\..\img
---

## Code Instrumentation {#sec:secInstrumentation}

Probably the first approach for doing performance analysis ever invented is code *instrumentation*. It is a technique that inserts extra code into a program to collect specific runtime information. [@lst:CodeInstrumentation] shows the simplest example of inserting a `printf` statement at the beginning of a function to indicate when this function is called. After that you run the program and count the number of times you see "foo is called" in the output. Perhaps, every programmer in the world did this at some point of their career at least once.

Listing: Code Instrumentation

~~~~ {#lst:CodeInstrumentation .cpp}
int foo(int x) {
+ printf("foo is called\n");
  // function body...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The plus sign at the beginning of a line means that this line was added and is not present in the original code. In general, instrumentation code is not meant to be pushed into the codebase, it's rather for collecting the needed data and then can be thrown away.

A slightly more interesting example of code instrumentation is presented in [@lst:CodeInstrumentationHistogram]. In this made-up code example, the function `findObject` searches for the coordinates of an object with some properties `p` on a map. The function `findObj` returns the confidence level of locating the right object with the current coordinates `c`. If it is an exact match, we stop the search loop and return the coordinates. If the confidence is above the `threshold`, we choose to `zoomIn` to find more precise location of the object. Otherwise, we get the new coordinates within the `searchRadius` to try our search next time.

Instrumentation code consists of two classes: `histogram` and `incrementor`. The former keeps track of whatever variable values we are interested in and frequencies of their occurence and then prints the histogram *after* the program finishes. The latter is just a helper class for pushing values into the `histogram` object. It is simple enough and can be adjusted to your specific needs quickly. I have a slightly more advanced version of this code which I usually copy-paste into whatever project I'm working on and then delete.

Listing: Code Instrumentation

~~~~ {#lst:CodeInstrumentationHistogram .cpp}
+ struct histogram {
+   std::map<uint32_t, std::map<uint32_t, uint64_t>> hist;
+   ~histogram() {
+     for (auto& tripCount : hist)
+       for (auto& zoomCount : tripCount.second)
+         std::cout << "[" << tripCount.first << "][" 
+                   << zoomCount.first << "] :  " 
+                   << zoomCount.second << "\n";
+   }
+ };
+ histogram h;

+ struct incrementor {
+   uint32_t tripCount = 0;
+   uint32_t zoomCount = 0;
+   ~incrementor() {
+ 	   h.hist[tripCount][zoomCount]++;
+   }
+ };

Coords findObject(const ObjParams& p, Coords c, float searchRadius) {
+ incrementor inc;
  while (true) {
+   inc.tripCount++;  
    float match = findObj(c, p);
    if (exactMatch(match))
      return c;   
    if (match > threshold) {
      searchRadius = zoomIn(c, searchRadius);
+     inc.zoomCount++;
    }
    c = getNewCoords(searchRadius);
  }
  return c;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this hypothetical scenario, we added instrumentation to know how frequently we `zoomIn` before we find an object. The variable `inc.tripCount` counts the number of iterations the loop runs before it exits, and the variable `inc.zoomCount` counts how many times we reduce the search radius. We always expect `inc.zoomCount` to be less or equal `inc.tripCount`. Here is the output one may observe after running the instrumented program:

```
[7][6]:  2
[7][5]:  6
[7][4]:  20
[7][3]:  156
[7][2]:  967
[7][1]:  3685
[7][0]:  251004
[6][5]:  2
[6][4]:  7
[6][3]:  39
[6][2]:  300
[6][1]:  1235
[6][0]:  91731
[5][4]:  9
[5][3]:  32
[5][2]:  160
[5][1]:  764
[5][0]:  34142
[4][4]:  5
[4][3]:  31
[4][2]:  103
[4][1]:  195
[4][0]:  14575
...
```

The first number in the square bracket is the trip count of the loop, and the second is the number of `zoomIn`s we made within the same loop. The number after the column sign is the number of occurences of that particular combination of the numbers. For example, two times we observed 7 loop iterations and 6 `zoomIn`s, 251004 times the loop ran 7 iterations and no `zoomIn`s, and so on. You can then plot the data for better visualization, employ some other statistical methods, but the main point we can make is that `zoomIn`s are not frequent. There were a total of 10k `zoomIn` calls for the 400k times that `findObject` was called. 

Later chapters of this book contain many examples of how such information can be used for data-driven optimizations. In our case, we conclude that `findObj` often fails to find the object. It means that the next iteration of the loop will try to find the object using new coordinates but still within the same search radius. Knowing that, we could attempt a number of optimizations: 1) run multiple searches in parallel, and synchronize if any of them succeeded; 2) precompute certain things for the current search region, thus eliminating repetitive work inside `findObj`; 3) write a software pipeline that calls `getNewCoords` to generate the next set of required coordinates and prefetch the corresponding map locations from memory. Part 2 of this book looks deeper into some of this techniques.

Code instrumentation provides very detailed information when you need specific knowledge about the execution of the program. It allows us to track any information about every variable in the program. Using such a method often yields the best insight when optimizing big pieces of code because you can use a top-down approach (instrumenting the main function then drilling down to its callees) of locating performance issues. While code instrumentation is not very helpful in the case of small programs, it gives the most value and insight by letting developers observe the architecture and flow of an application. This technique is especially helpful for someone working with an unfamiliar codebase.

It's also worth mentioning that code instrumentation shines in complex systems with many different components that react differently based on inputs or over time. For example, in games, usually, there is a renderer thread, a physics thread, an animations thread, etc. Instrumenting such big modules helps to reasonably quickly understand what module is the source of issues. As sometimes, optimizing is not only a matter of optimizing code but also data. For example, rendering might be too slow because of uncompressed mesh, or physics might be too slow because of too many objects in a scene.

The instrumentation technique is heavily used in performance analysis of real-time scenarios, such as video games and embedded development. Some profilers combine instrumentation with other techniques such as tracing or sampling. We will look at one such hybrid profilers called Tracy in [@sec:Tracy].

While code instrumentation is powerful in many cases, it does not provide any information about how code executes from the OS or CPU perspective. For example, it can't give you information about how often the process was scheduled in and out of execution (known by the OS) or how many branch mispredictions occurred (known by the CPU). Instrumented code is a part of an application and has the same privileges as the application itself. It runs in userspace and doesn't have access to the kernel.

A more important downside of this technique is that every time something new needs to be instrumented, say another variable, recompilation is required. This can become a burden and increase analysis time. Unfortunately, there are additional downsides. Since usually, you care about hot paths in the application, you're instrumenting the things that reside in the performance-critical part of the code. Injecting instrumentation code in a hot path might easily result in a 2x slowdown of the overall benchmark. Remember not to benchmark an instrumented program. Because by instrumenting the code, you change the behavior of the program, so you might not see the same effects you saw earlier.

All of the above increases time between experiments and consumes more development time, which is why engineers don't manually instrument their code very often these days. However, automated code instrumentation is still widely used by compilers. Compilers are capable of automatically instrumenting an entire program (except third-party libraries) to collect interesting statistics about the execution. The most widely known use cases for automated instrumentation are code coverage analysis and Profile Guided Optimizations (see [@sec:secPGO]).

When talking about instrumentation, it's important to mention binary instrumentation techniques. The idea behind binary instrumentation is similar but it is done on an already-built executable file rather than on source code. There are two types of binary instrumentation: static (done ahead of time) and dynamic (instrumented code is inserted on-demand as a program executes). The main advantage of dynamic binary instrumentation is that it does not require program recompilation and relinking. Also, with dynamic instrumentation, one can limit the amount of instrumentation to only interesting code regions, instead of instrumenting the entire program.

Binary instrumentation is very useful in performance analysis and debugging. One of the most popular tools for binary instrumentation is the Intel [Pin](https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool)[^1] tool. Pin intercepts the execution of a program at the occurrence of an interesting event and generates new instrumented code starting at this point in the program. This enables the collecting of various runtime information, for example: 

[TODO]: add discussion on SDE?

* instruction count and function call counts. 
* intercepting function calls and execution of any instruction in an application.
* allows "record and replay" the program region by capturing the memory and HW registers state at the beginning of the region.

Like code instrumentation, binary instrumentation enables instrumenting only user-level code and can be very slow.

[^1]: PIN - [https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool](https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool)
