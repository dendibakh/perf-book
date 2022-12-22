---
typora-root-url: ..\..\img
---

# Optimizing Memory Accesses

## CPU Back-End Optimizations

CPU Back-End (BE) component is discussed in [@sec:uarchBE]. Most of the time, inefficiencies in CPU BE can be described as a situation when FE has fetched and decoded instructions, but BE is overloaded and can't handle new instructions. Technically speaking, it is a situation when FE cannot deliver uops due to a lack of required resources for accepting new uops in the Backend. An example of it may be a stall due to data-cache miss or a stall due to the divider unit being overloaded.

I want to emphasize to the reader that it's recommended to start looking into optimizing code for CPU BE only when TMA points to a high "Back-End Bound" metric. TMA further divides the `Backend Bound` metric into two main categories: `Memory Bound` and `Core Bound`, which we will discuss next.
