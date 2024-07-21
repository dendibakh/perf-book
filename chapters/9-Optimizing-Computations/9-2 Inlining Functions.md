## Inlining Functions

If you're one of those developers who frequently looks into assembly code, you have probably seen `CALL`, `PUSH`, `POP`, and `RET` instructions. In x86 ISA, `CALL` and `RET` instructions are used to call and return from a function. `PUSH` and `POP` instructions are used to save a register value on the stack and restore it.

The nuances of a function call are described by the *calling convention*, how arguments are passed and in what order, how the result is returned, which registers the called function must preserve, and how the work is split between the caller and the callee. Based on a calling convention, when a caller makes a function call, it expects that some registers will hold the same values after the callee returns. Thus, if a callee needs to change one of the registers that should be preserved, it needs to save (`PUSH`) and restore (`POP`) them before returning to the caller. A series of `PUSH` instructions is called a *prologue*, and a series of `POP` instructions is called an *epilogue*.

When a function is small, the overhead of calling a function (prologue and epilogue) can be very pronounced. This overhead can be eliminated by inlining a function body into the place where it was called. Function inlining is a process of replacing a call to function `foo` with the code for `foo` specialized with the actual arguments of the call. Inlining is one of the most important compiler optimizations. Not only because it eliminates the overhead of calling a function, but also because it enables other optimizations. This happens because when a compiler inlines a function, the scope of compiler analysis widens to a much larger chunk of code. However, there are disadvantages as well: inlining can potentially increase code size and compile time.[^20]

The primary mechanism for function inlining in many compilers relies on a cost model. For example, in the LLVM compiler, function inlining is based on computing a cost for each function *call site*. A call site is a place in the code where a function is called. The cost of inlining a function call is based on the number and type of instructions in that function. Inlining happens if the cost is less than a threshold, which is usually fixed; however, it can be varied under certain circumstances.[^21] In addition to the generic cost model, many heuristics can overwrite cost model decisions in some cases. For instance: 

* Tiny functions (wrappers) are almost always inlined.
* Functions with a single call site are preferred candidates for inlining.
* Large functions usually are not inlined as they bloat the code of the caller function.

Also, there are situations when inlining is problematic:

* A recursive function cannot be inlined into itself unless it's a tail-recursive function (see next section). Also, if the depth of recursion is usually small, it's possible to partially inline a recursive function, i.e., inline a body of a recursive function to itself a couple of times, and then leave a recursive call as before. This may eliminate the overhead of a function call in the common case.
* A function that is referred to through a pointer can be inlined in place of a direct call but the function has to remain in the binary, i.e., it cannot be fully inlined and eliminated. The same is true for functions with external linkage.

As we said earlier, compilers tend to use a cost model approach when deciding about inlining a function, which typically works well in practice. In general, it is a good strategy to rely on the compiler for making all the inlining decisions and adjusting if needed. The cost model cannot account for every possible situation, which leaves room for improvement. Sometimes compilers require special hints from the developer. One way to find potential candidates for inlining in a program is by looking at the profiling data, and in particular, how hot is the prologue and the epilogue of the function. [@lst:FuncInlining] is an example of a function profile with a prologue and epilogue consuming `~50%` of the function time:

Listing: A profile of function `foo` which has a hot prologue and epilogue

~~~~ {#lst:FuncInlining .cpp}
Overhead |  Source code & Disassembly
   (%)   |  of function `foo`
--------------------------------------------
    3.77 :  418be0:  push   r15	     # prologue
    4.62 :  418be2:  mov    r15d,0x64
    2.14 :  418be8:  push   r14
    1.34 :  418bea:  mov    r14,rsi
    3.43 :  418bed:  push   r13
    3.08 :  418bef:  mov    r13,rdi
    1.24 :  418bf2:  push   r12
    1.14 :  418bf4:  mov    r12,rcx
    3.08 :  418bf7:  push   rbp
    3.43 :  418bf8:  mov    rbp,rdx
    1.94 :  418bfb:  push   rbx
    0.50 :  418bfc:  sub    rsp,0x8
    ...
    # function body
    ...
    4.17 :  418d43:  add    rsp,0x8  # epilogue
    3.67 :  418d47:  pop    rbx
    0.35 :  418d48:  pop    rbp
    0.94 :  418d49:  pop    r12
    4.72 :  418d4b:  pop    r13
    4.12 :  418d4d:  pop    r14
    0.00 :  418d4f:  pop    r15
    1.59 :  418d51:  ret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you see hot `PUSH` and `POP` instructions, this might be a strong indicator that the time consumed by the prologue and epilogue of the function might be saved if we inline the function. Note that even if the prologue and epilogue are hot, it doesn't necessarily mean it will be profitable to inline the function. Inlining triggers a lot of different changes, so it's hard to predict the outcome. Always measure the performance of the changed code before forcing a compiler to inline a function.

For the GCC and Clang compilers, you can make a hint for inlining `foo` with the help of a C++11 `[[gnu::always_inline]]` attribute as shown in the code example below. If using those compilers with earlier C++ standards you can use `__attribute__((always_inline))`. For the MSVC compiler, you can use the `__forceinline` keyword.

```cpp
[[gnu::always_inline]] int foo() {
    // foo body
}
```

### Tail Call Optimization

In a tail-recursive function, the recursive call is the last operation performed by the function before it returns its result. A simple example is demonstrated [@lst:TailCall]. In the original code, the `sum` function recursively accumulates integer numbers from 0 to `n, for example, a call of `sum(5,0)` will yield `5+4+3+2+1`, which gives 15.

If we compile the original code without optimizations (`-O0`), compilers will generate assembly code that has a recursive call. This is very inefficient due to the overhead of the function call. Moreover, if you call `sum` with a large `n`, then there is a high chance that it will result in a stack overflow since the stack memory is limited.

When you apply optimizations, e.g., `-O2`, to the example in [@lst:TailCall], compilers will recognize an opportunity for tail call optimization. The transformation will reuse the current stack frame instead of recursively creating new frames. To do so, the compiler flushes the current frame and replaces the `call` instruction with `jmp` at the beginning of the function. Just like inlining, tail call optimization provides room for further optimizations. So, later, the compiler can apply more transformations to replace the original version with an iterative version shown on the right. For example, GCC 13.2 generates identical machine code for both versions.

Listing: Tail Call Compiler Optimization
		
~~~~ {#lst:TailCall .cpp}
// original code                         // compiler intermediate transformation
int sum(int n, int acc) {                int sum(int n, int acc) {
  if (n == 0) {                            for (int i = n; i > 0; --i) {
    return acc;                    =>        acc += i;
  } else {                                 }
    return sum(n - 1, acc + n);            return acc;
  }                                      }
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like with any compiler optimization, there are cases when it cannot perform the code transformation you want. If you are using the Clang compiler, and you want guaranteed tail call optimizations, you can mark a `return` statement with `__attribute__((musttail))`. This indicates that the compiler must generate a tail call for the program to be correct, even when optimizations are disabled. One example, where it is beneficial is language interpreter loops.[^22] In case of doubt, it is better to use an iterative version instead of tail recursion and leave tail recursion to functional programming languages.

[^20]: See the article: [https://aras-p.info/blog/2017/10/09/Forced-Inlining-Might-Be-Slow/](https://aras-p.info/blog/2017/10/09/Forced-Inlining-Might-Be-Slow/).
[^21]: For example: 1) when a function declaration has a hint for inlining; 2) when there is profiling data for the function; or 3) when a compiler optimizes for size (`-Os`) rather than performance (`-O2`).
[^22]: Josh Haberman's blog: motivation for guaranteed tail calls - [https://blog.reverberate.org/2021/04/21/musttail-efficient-interpreters.html](https://blog.reverberate.org/2021/04/21/musttail-efficient-interpreters.html).