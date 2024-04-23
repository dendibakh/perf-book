---
typora-root-url: ..\..\img
---

## Inlining Functions

If you're one of those developers who frequently looks into assembly code, you have probably seen `CALL`, `PUSH`, `POP`, and `RET` instructions. In x86 ISA, `CALL` and `RET` instructions are used to call and return from a function. `PUSH` and `POP` instructions are used to save a register value on the stack and restore it back.

The nuances of a function call are described by the *calling convention*, how arguments are passed and in what order, how the result is returned, which registers the called function must preserve and how the work is split between the caller and the callee. Based on a calling convention, when a caller makes a function call, it expects that some registers will hold the same values after the callee returns. Thus, if a callee needs to change one of the registers that should be preserved, it needs to save (`PUSH`) and restore (`POP`) them before returning to the caller. A series of `PUSH` instructions is called a *prologue*, and a series of `POP` instructions is called an *epilogue*.

When a function is small, overhead of calling a function (prologue and epilogue) can be very pronounced. This overhead can be eliminated by inlining a function body into the place where it was called. Function inlining is a process of replacing a call to a function `F` with the code for `F` specialized with the actual arguments of the call. Inlining is one of the most important compiler optimizations. Not only because it eliminates the overhead of calling a function, but also it enables other optimizations. This happens because when a compiler inlines a function, the scope of compiler analysis widens to a much larger chunk of code. However, there are disadvantages as well: inlining can potentially increase the code size and compile time[^20].

The primary mechanism for function inlining in many compilers relies on a cost model. For example, in the LLVM compiler, it is based on computing a cost for each function call (callsite). The cost of inlining a function call is based on the number and type of instructions in that function. Inlining happens if the cost is less than a threshold, which is usually fixed; however, it can be varied under certain circumstances.[^21] In addition to the generic cost model, there are many heuristics that can overwrite cost model decisions in some cases. For instance: 

* Tiny functions (wrappers) are almost always inlined.
* Functions with a single callsite are preferred candidates for inlining.
* Large functions usually are not inlined as they bloat the code of the caller function.

Also, there are situations when inlining is problematic:

* A recursive function cannot be inlined into itself.
* A function that is referred to through a pointer can be inlined in place of a direct call but the functiona has to remain in the binary, i.e., it cannot be fully inlined and eliminated. The same is true for functions with external linkage.

As we said earlier, compilers tend to use a cost model approach when making a decision about inlining a function, which typically works well in practice. In general, it is a good strategy to rely on the compiler for making all the inlining decisions and adjust if needed. The cost model cannot account for every possible situation, which leaves room for improvement. Sometimes compilers require special hints from the developer. One way to find potential candidates for inlining in a program is by looking at the profiling data, and in particular, how hot is the prologue and the epilogue of the function. Below is an example of a function profile with prologue and epilogue consuming `~50%` of the function time:

```bash
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
    #                                # function body
    ...
    4.17 :  418d43:  add    rsp,0x8	 # epilogue
    3.67 :  418d47:  pop    rbx
    0.35 :  418d48:  pop    rbp
    0.94 :  418d49:  pop    r12
    4.72 :  418d4b:  pop    r13
    4.12 :  418d4d:  pop    r14
    0.00 :  418d4f:  pop    r15
    1.59 :  418d51:  ret

```

When you see hot `PUSH` and `POP` instructions, this might be a strong indicator that the time consumed by the prologue and epilogue of the function might be saved if we inline the function. Note that even if the prologue and epilogue are hot, it doesn't necessarily mean it will be profitable to inline the function. Inlining triggers a lot of different changes, so it's hard to predict the outcome. Always measure the performance of the changed code before forcing compiler to inline a function.

For GCC and Clang compilers, one can make a hint for inlining `foo` with the help of C++11 `[[gnu::always_inline]]` attribute as shown in the code example below. For earlier C++ standards one can use `__attribute__((always_inline))`. For the MSVC compiler, one can use the `__forceinline` keyword.

```cpp
[[gnu::always_inline]] int foo() {
    // foo body
}
```

### Tail call optimization

A tail recursive function is a function that as last call (tail) does `return function(...)`. This is demonstrated in the following example:

```cpp
int sum(int n, int accumulator)
{
    if (n == 0)
    {
        return accumulator;
    }
    else
    {
        return sum(n - 1, accumulator + n);
    }
}
```

The sum method recursivly adds `n` to each number below `n`. To calculate the sum of 5, call `sum(5,0)` and `5+4+3+2+1` is calulated which gives 15.

After compiling using GCC and without optimizations, from the generated assembly it is clear that the assembly of the sum function is recursive because it calls itself:

```asm
sum(int, int):                               # @sum(int, int)
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        mov     dword ptr [rbp - 8], edi
        mov     dword ptr [rbp - 12], esi
        cmp     dword ptr [rbp - 8], 0
        jne     .LBB0_2
        mov     eax, dword ptr [rbp - 12]
        mov     dword ptr [rbp - 4], eax
        jmp     .LBB0_3
.LBB0_2:
        mov     edi, dword ptr [rbp - 8]
        sub     edi, 1
        mov     esi, dword ptr [rbp - 12]
        add     esi, dword ptr [rbp - 8]
        call    sum(int, int)                   ; self call
        mov     dword ptr [rbp - 4], eax
.LBB0_3:
        mov     eax, dword ptr [rbp - 4]
        add     rsp, 16
        pop     rbp
        ret
```

This is very inefficient due to the overhead of the function call. It also limits the number of recursive calls that can be made before exceeding the stack limit.

But when applying some optimization options, the compiler could decide to apply the tail call optimization and replace the recursive version, by an iterative one. The following code is generated using GCC with O2.

```asm
sum(int, int):
        mov     eax, esi
        test    edi, edi
        je      .L5
        lea     edx, [rdi-1]
        test    dil, 1
        je      .L2
        add     eax, edi
        mov     edi, edx
        test    edx, edx
        je      .L17
.L2:
        lea     eax, [rax-1+rdi*2]
        sub     edi, 2
        jne     .L2
.L5:
        ret
.L17:
        ret
```

It is clear from the above assembly that function isn't recursive any longer since there is no `call    sum(int, int)`. Just like inlining, the tail call optimization provides room for further optimization.

Unfortunately, one can't rely blindly on the tail call optimization and inspection of generated assembly as required. There are compiler specific extensions like `__attribute__((musttail))` from Clang. In case of doubt, it is better to use an iterative version instead of tail resursion and leave tail recursion to functional programming languagues.

[^20]: See the article: [https://aras-p.info/blog/2017/10/09/Forced-Inlining-Might-Be-Slow/](https://aras-p.info/blog/2017/10/09/Forced-Inlining-Might-Be-Slow/).
[^21]: For example, 1) when a function declaration has a hint for inlining, 2) when there is profiling data for the function, or 3) when a compiler optimizes for size (`-Os`) rather than performance (`-O2`).
