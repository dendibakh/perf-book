---
typora-root-url: ..\..\img
---

## Software and Hardware Timers {#sec:timers}

To benchmark execution time, engineers usually use two different timers, which all the modern platforms provide:

 - **System-wide high-resolution timer**. This is a system timer that is typically implemented as a simple count of the number of ticks that have transpired since an arbitrary starting date, called the [epoch](https://en.wikipedia.org/wiki/Epoch_(computing))[^1]. This clock is monotonic; i.e., it always goes up. System time can be retrieved from the OS with a system call[^2]. Accessing the system timer on Linux systems is possible via the `clock_gettime` system call. System timer has a nano-seconds resolution, is consistent between all the CPUs and is independent of CPU frequency. Even though the system timer can return timestamps with nano-seconds accuracy, it is not suitable for measuring short running events because it takes a long time to obtain the timestamp via the `clock_gettime` system call. But it is OK to measure events with a duration of more than a microsecond. The `de facto` standard for accessing system timer in C++ is using `std::chrono` as shown in [@lst:Chrono].

   Listing: Using C++ std::chrono to access system timer
   
   ~~~~ {#lst:Chrono .cpp}
   #include <cstdint>
   #include <chrono>

   // returns elapsed time in nanoseconds
   uint64_t timeWithChrono() {
     using namespace std::chrono;
     auto start = steady_clock::now();
     // run something
     auto end = steady_clock::now();
     uint64_t delta = duration_cast<nanoseconds>
         (end - start).count();
     return delta;
   }
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
 - **Time Stamp Counter (TSC)**. This is an HW timer which is implemented as an HW register. TSC is monotonic and has a constant rate, i.e., it doesn't account for frequency changes. Every CPU has its own TSC, which is simply the number of reference cycles (see [@sec:secRefCycles]) elapsed. It is suitable for measuring short events with a duration from nanoseconds and up to a minute. The value of TSC can be retrieved by using compiler built-in function `__rdtsc` as shown in [@lst:TSC], which uses `RDTSC` assembly instruction under the hood. More low-level details on benchmarking the code using `RDTSC` assembly instruction can be accessed in a white paper [@IntelRDTSC].

   Listing: Using __rdtsc compiler builtins to access TSC

   ~~~~ {#lst:TSC .cpp}
   #include <x86intrin.h>
   #include <cstdint>

   // returns the number of elapsed reference clocks
   uint64_t timeWithTSC() {
       uint64_t start = __rdtsc();
       // run something
       return __rdtsc() - start;
   }
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choosing which timer to use is very simple and depends on how long the thing is that you want to measure. If you measure something over a very small time period, TSC will give you better accuracy. Conversely, it's pointless to use the TSC to measure a program that runs for hours. Unless you really need cycle accuracy, the system timer should be enough for a large proportion of cases. It's important to keep in mind that accessing system timer usually has higher latency than accessing TSC. Making a `clock_gettime` system call can be easily ten times slower than executing `RDTSC` instruction, which takes 20+ CPU cycles. This may become important for minimizing measurement overhead, especially in the production environment. Performance comparison of different APIs for accessing timers on various platforms is available on [wiki page](https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis)[^3] of CppPerformanceBenchmarks repository.

[^1]: Unix epoch starts at 1 January 1970 00:00:00 UT: [https://en.wikipedia.org/wiki/Unix_epoch](https://en.wikipedia.org/wiki/Unix_epoch).
[^2]: Retrieving system time - [https://en.wikipedia.org/wiki/System_time#Retrieving_system_time](https://en.wikipedia.org/wiki/System_time#Retrieving_system_time)
[^3]: CppPerformanceBenchmarks wiki - [https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis](https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis)
