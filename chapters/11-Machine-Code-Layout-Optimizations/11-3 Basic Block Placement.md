---
typora-root-url: ..\..\img
---

## Basic Block Placement {#sec:secLIKELY}

Suppose we have a hot path in the program that has some error handling code (`coldFunc`) in between:

```cpp
// hot path
if (cond)
  coldFunc();
// hot path again
```
Figure @fig:BBLayout shows two possible physical layouts for this snippet of code. Figure @fig:BB_default is the layout most compiler will emit by default, given no hints provided. The layout that is shown in Figure @fig:BB_better can be achieved if we invert the condition `cond` and place hot code as fall through.

<div id="fig:BBLayout">
![default layout](../../img/cpu_fe_opts/BBLayout_Default.jpg){#fig:BB_default width=30%}
![improved layout](../../img/cpu_fe_opts/BBLayout_Better.jpg){#fig:BB_better width=30%}

Two different machine code layouts.
</div>

Which layout is better in the common case greatly depends on whether `cond` is usually true or not. If `cond` is usually true, then we would better choose the default layout because otherwise, we would be doing two jumps instead of one. Also, in the general case, we want to inline the function that is guarded under `cond`. However, in this particular example, we know that coldFunc is an error handling function and is likely not executed very often. By choosing layout @fig:BB_better, we maintain fall through between hot pieces of the code and convert taken branch into not taken one.

There are a few reasons why for the code presented earlier in this section, layout @fig:BB_better performs better. First of all, not taken branches are fundamentally cheaper than taken. In the general case, modern Intel CPUs can execute two untaken branches per cycle but only one taken branch every two cycles. [^2]

Secondly, layout @fig:BB_better makes better use of the instruction and uop-cache (DSB, see [@sec:uarchFE]). With all hot code contiguous, there is no cache line fragmentation: all the cache lines in the L1I-cache are used by hot code. The same is true for the uop-cache since it caches based on the underlying code layout as well. 

Finally, taken branches are also more expensive for the fetch unit. It fetches contiguous chunks of 16 bytes, so every taken jump means the bytes after the jump are useless. This reduces the maximum effective fetch throughput.

To suggest a compiler to generate an improved version of the machine code layout, one can provide a hint using [`__builtin_expect`](https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect)[^3] construct: 

```cpp
// hot path
if (__builtin_expect(cond, 0)) // NOT likely to be taken
  coldFunc();
// hot path again
```

Developers usually write `LIKELY` helper macros to make the code more readable, so more often, you can find the code that looks like the one shown below. Since C++20, there is a standard `[[likely]]`[^10] attribute, which should be preferred.

```cpp
#define LIKELY(EXPR)   __builtin_expect((bool)(EXPR), true)
#define UNLIKELY(EXPR) __builtin_expect((bool)(EXPR), false)

if (LIKELY(ptr != nullptr))
  // do something with ptr
```

Optimizing compilers will not only improve code layout when they encounter `LIKELY/UNLIKELY` hints. They will also leverage this information in other places. For example, when `UNLIKELY` hint is applied to our original example in this section, the compiler will prevent inlining `coldFunc` as it now knows that it is unlikely to be executed often and it's more beneficial to optimize it for size, i.e., just leave a `CALL` to this function. Inserting `__builtin_expect` hint is also possible for a switch statement as presented in [@lst:BuiltinSwitch].

Listing: Built-in expect hint for switch statement

~~~~ {#lst:BuiltinSwitch .cpp}
for (;;) {
  switch (__builtin_expect(instruction, ADD)) {
    // handle different instructions
  }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using this hint, a compiler will be able to reorder code a little bit differently and optimize the hot switch for faster processing `ADD` instructions. More details about this transformation is available on [easyperf](https://easyperf.net/blog/2019/11/22/data-driven-tuning-specialize-switch)[^9] blog.

[^2]: There is a special small loop optimization that allows very small loops to have one taken branch per cycle.
[^3]: More about builtin-expect here: [https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect](https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect).
[^9]: Using `__builtin_expect` for a switch statement - [https://easyperf.net/blog/2019/11/22/data-driven-tuning-specialize-switch](https://easyperf.net/blog/2019/11/22/data-driven-tuning-specialize-switch).
[^10]: C++ standard `[[likely]]` attribute: [https://en.cppreference.com/w/cpp/language/attributes/likely](https://en.cppreference.com/w/cpp/language/attributes/likely).

