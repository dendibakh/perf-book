### Microarchitecture-Specific Performance Issues {#sec:UarchSpecificIssues}

#### Memory Order Violations {.unlisted .unnumbered}

We introduced the concept of memory ordering in [@sec:uarchLSU]. Memory reordering is a crucial aspect of modern CPUs, as it allows to execute memory requests in parallel and out-of-order. The key element in load/store reordering is memory disambiguation, which predicts if it is safe to let loads go ahead of earlier stores. Since the memory disambiguation is speculative, it can lead to performance issues if not handled properly.

Consider an example in [@lst:MemOrderViolation], on the left. This code snippet calculates a histogram of an 8-bit grayscale image, i.e., calculate how many times a certain color appears in the image. Besides countless other places, this code can be found in Otsu's thresholding algorithm[^1] that is used to convert a grayscale image to a binary image. Since the input image is 8-bit grayscale, there are only 256 different colors. 

For each pixel on an image, you need to read the current histogram count of the color of the pixel, increment it and store it back. This is a classic read-modify-write dependency through the memory. Imagine we have the following consequtive pixels in the image: `0xFF 0xFF 0x00 0xFF 0xFF ...` and so on. The loaded value of the histogram count for pixel 1 comes from the result of the previous iteration. But the histogram count for pixel 2 comes from memory; it is independent and can be reordered. But then again, the histogram count for pixel 3 is dependent on the result of processing pixel 1, and so on. 

Listing: Memory Order Violation Example.

~~~~ {#lst:MemOrderViolation .cpp}
std::array<uint32_t, 256> hist;                    std::array<uint32_t, 256> hist1;
hist.fill(0);                                      std::array<uint32_t, 256> hist2;
for (int i = 0; i < width * height; ++i)     =>    hist1.fill(0);
  hist[image[i]]++;                                hist2.fill(0);
                                                   int i = 0;
                                                   for (; i + 1 < width * height; i += 2) {
                                                     hist1[image[i+0]]++;
                                                     hist2[image[i+1]]++;
                                                   }
                                                   for (; i < width * height; ++i)
                                                     hist1[image[i]]++;

                                                   for (int i = 0; i < hist1.size(); ++i)
                                                     hist1[i] += hist2[i];
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recall from [@sec:uarchLSU], the processor doesn't necessarily knows about a potential store-to-load forwarding, so it has to predict. If it correctly predicts a memory order violation between two updates of color `0xFF`, then these accesses will be serialized. The performance will not be great, but it is the best outcome we could hope for with the initial code. On the contrary, if the processor predicts that there is no memory order violation, it will speculatively make the two updates in parallel. Later it will recognize the mistake, flush the pipeline, and re-execute the later of the two updates. This is a performance worst-case scenario.


When updates of the same color in the histogram occur at relatively high rates, the processor may not have completed updating pixel i prior to beginning pixel i+1. In such cases, a processor predicts whether the value loaded for the i+1 update will come from memory or from the i's store. If from memory, the two updates can be performed in parallel, otherwise the processor must serialize the updates.

If repeated accesses to particular elements in the data structure sometimes (but not always) occur "close" to each other, temporally, then memory ordering violations and subsequent pipeline flushes can occur as a result of these accesses. 

Note that “close” in this context means within the core’s out-of-order instruction window: repeated readmodify-writes of the same element may trigger ordering violations if they occur within a few loop iterations of each other, but not if they occur hundreds or thousands of loop iterations apart.
Here are several types of data structures from real algorithm

[TODO]: add a link to the lab
https://github.com/dendibakh/perf-ninja/tree/main/labs/memory_bound/mem_order_violation_1

#### Memory alignment {.unlisted .unnumbered}

The cores support unaligned accesses to normal, cacheable memory for all available
data sizes. When executed sporadically, unaligned accesses generally complete without
any observable performance impact to overall execution. Some accesses will suffer
delays, however, and the impact is often greater for stores than loads

example with split loads in matmul

#### 4K aliasing {.unlisted .unnumbered}

just describe
https://richardstartin.github.io/posts/4k-aliasing
While unlikely to be a significant
problem, L1I Cache misses may result from set conflicts. Apple silicon uses 16KB
memory pages that may make this even more likely to occur, since independent
libraries tend to be aligned to page boundaries when they are loaded.

#### Cache trashing {.unlisted .unnumbered}

just describe
Avoid Cache Thrashing: Minimize cache conflicts by ensuring data structures do not excessively map to the same cache lines.
https://github.com/ibogosavljevic/hardware-efficiency/blob/main/cache-conflicts/cache_conflicts.c

#### Non-Temporal Loads and Stores {.unlisted .unnumbered}

Caches naturally store data close to the processor under the assumption that the data in
the cache line will be used again in the near term. Data that benefits from caching is said
to have temporal locality. However, some algorithms stream (read and/or write) through
large quantities of data with little temporal reuse. In these cases, storing the data in the
cache is counterproductive because it floods (or "pollutes") the cache with unneeded
data, forcing out potentially useful data.
When using Non-Temporal Loads and Stores, the processor will optimize cache allocation
policies for particular cache lines to minimize pollution.
These special assembly instructions usually have "NT" suffix.

https://www.agner.org/optimize/optimizing_cpp.pdf#page=108&zoom=100,116,716

#### Store-to-Load Forwarding Delays {.unlisted .unnumbered}

#### Minimize Moves Between Integer and Floating-Point Registers {.unlisted .unnumbered}

DUP(general), FMOV(general), INS(general), MOV(from general), SCVTF(scalar), UCVTF(scalar)
Movement of data between integer and vector registers requires several cycles. Load
directly into vector registers
In most of the cases it is compiler's job to ensure, but in case you're writing compiler intrinsics or inline assembly routines, this advice may become handy.
When you need to load a `uint32_t` value from memory and then convert it to `float`, do not load the value in a general-purpose register (e.g. `EAX`) and then convert it to `XMM0`; load straight into `XMM0`.

Also, avoid mixing single and double precision values. For example:
```cpp
float circleLength(float r) {
    //return 2.0 * 3.14 * r; // 
    return 2.0f * 3.14f * r;
}
```

#### Slow Floating-Point Arithmetic {.unlisted .unnumbered}

#### AVX-SSE Transitions {.unlisted .unnumbered}

remove?
https://www.agner.org/optimize/microarchitecture.pdf#page=167&zoom=100,116,904

[^1]: Otsu's thresholding method - [https://en.wikipedia.org/wiki/Otsu%27s_method](https://en.wikipedia.org/wiki/Otsu%27s_method)
