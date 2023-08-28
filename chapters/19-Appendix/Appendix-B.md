---
typora-root-url: ..\..\img
---

# Appendix B. The LLVM Vectorizer {.unnumbered}

\markright{Appendix B}

This section describes the state of the LLVM Loop Vectorizer inside the Clang compiler as of the year 2020. Innerloop vectorization is the process of transforming code in the innermost loops into code that uses vectors across multiple loop iterations. Each lane in the SIMD vector performs independent arithmetic on consecutive loop iterations. Usually, loops are not found in a clean state, and the Vectorizer has to guess and assume missing information and check for details at runtime. If the assumptions are proven wrong, the Vectorizer falls back to running the scalar loop. The examples below highlight some of the code patterns that the LLVM Vectorizer supports. 

## Loops with unknown trip count {.unnumbered .unlisted}

The LLVM Loop Vectorizer supports loops with an unknown trip count. In the loop below, the iteration start and finish points are unknown, and the Vectorizer has a mechanism to vectorize loops that do not start at zero. In this example, `n` may not be a multiple of the vector width, and the Vectorizer has to execute the last few iterations as scalar code. Keeping a scalar copy of the loop increases the code size.

```cpp
void bar(float* A, float* B, float K, int start, int end) {
  for (int i = start; i < end; ++i)
    A[i] *= B[i] + K;
}
```

## Runtime Checks of Pointers {.unnumbered .unlisted}

In the example below, if the pointers A and B point to consecutive addresses, then it is illegal to vectorize the code because some elements of A will be written before they are read from array B.

Some programmers use the `restrict` keyword to notify the compiler that the pointers are disjointed, but in our example, the LLVM Loop Vectorizer has no way of knowing that the pointers A and B are unique. The Loop Vectorizer handles this loop by placing code that checks, at runtime, if the arrays A and B point to disjointed memory locations. If arrays A and B overlap, then the scalar version of the loop is executed.

```cpp
void bar(float* A, float* B, float K, int n) {
  for (int i = 0; i < n; ++i)
    A[i] *= B[i] + K;
}
```

## Reductions {.unnumbered .unlisted}

In this example, the sum variable is used by consecutive iterations of the loop. Normally, this would prevent vectorization, but the Vectorizer can detect that `sum` is a reduction variable. The variable `sum` becomes a vector of integers, and at the end of the loop, the elements of the array are added together to create the correct result. The LLVM Vectorizer supports a number of different reduction operations, such as addition, multiplication, XOR, AND, and OR.

```cpp
int foo(int *A, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
    sum += A[i] + 5;
  return sum;
}
```


The LLVM Vectorizer supports floating-point reduction operations when `-ffast-math` is used.

## Inductions {.unnumbered .unlisted}

In this example, the value of the induction variable i is saved into an array. The LLVM Loop Vectorizer knows to vectorize induction variables.

```cpp
void bar(float* A, int n) {
  for (int i = 0; i < n; ++i)
    A[i] = i;
}
```

## If Conversion {.unnumbered .unlisted}

The LLVM Loop Vectorizer is able to “flatten” the IF statement in the code and generate a single stream of instructions. The Vectorizer supports any control flow in the innermost loop. The innermost loop may contain complex nesting of IFs, ELSEs, and even GOTOs.

```cpp
int foo(int *A, int *B, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
    if (A[i] > B[i])
      sum += A[i] + 5;
  return sum;
}
```

## Pointer Induction Variables {.unnumbered .unlisted}

This example uses the `std::accumulate` function from the standard c++ library. This loop uses C++ iterators, which are pointers, and not integer indices. The LLVM Loop Vectorizer detects pointer induction variables and can vectorize this loop. This feature is important because many C++ programs use iterators.

```cpp
int baz(int *A, int n) {
  return std::accumulate(A, A + n, 0);
}
```

## Reverse Iterators {.unnumbered .unlisted}

The LLVM Loop Vectorizer can vectorize loops that count backward.

```cpp
int foo(int *A, int n) {
  for (int i = n; i > 0; --i)
    A[i] +=1;
}
```

## Scatter / Gather {.unnumbered .unlisted}

The LLVM Loop Vectorizer can vectorize code that becomes a sequence of scalar instructions that scatter/gathers memory.

```cpp
int foo(int * A, int * B, int n) {
  for (intptr_t i = 0; i < n; ++i)
      A[i] += B[i * 4];
}
```

In many situations, the cost model will decide that this transformation is not profitable. 

## Vectorization of Mixed Types {.unnumbered .unlisted}

The LLVM Loop Vectorizer can vectorize programs with mixed types. The Vectorizer cost model can estimate the cost of the type conversion and decide if vectorization is profitable.

```cpp
int foo(int *A, char *B, int n) {
  for (int i = 0; i < n; ++i)
    A[i] += 4 * B[i];
}
```

## Vectorization of function calls {.unnumbered .unlisted}

The LLVM Loop Vectorizer can vectorize intrinsic math functions. See the table below for a list of these functions.

```bash
pow        exp        exp2
sin        cos        sqrt
log        log2       log10
fabs       floor      ceil
fma        trunc      nearbyint
fmuladd
```

## Partial unrolling during vectorization {.unnumbered .unlisted}

Modern processors feature multiple execution units, and only programs that contain a high degree of parallelism can fully utilize the entire width of the machine. The LLVM Loop Vectorizer increases the instruction-level parallelism (ILP) by performing partial-unrolling of loops.

In the example below, the entire array is accumulated into the variable `sum`. This is inefficient because only a single execution port can be used by the processor. By unrolling the code, the Loop Vectorizer allows two or more execution ports to be used simultaneously.

```cpp
int foo(int *A, int n) {
  unsigned sum = 0;
  for (int i = 0; i < n; ++i)
      sum += A[i];
  return sum;
}
```


The LLVM Loop Vectorizer uses a cost model to decide when it is profitable to unroll loops. The decision to unroll the loop depends on the register pressure and the generated code size.

## SLP vectorization {.unnumbered .unlisted}

SLP (Superword-Level Parallelism) vectorizer tries to glue multiple scalar operations together into vector operations.  It processes the code bottom-up, across basic blocks, in search of scalars to combine. The goal of SLP vectorization is to combine similar independent instructions into vector instructions. Memory accesses, arithmetic operations, comparison operations can all be vectorized using this technique. For example, the following function performs very similar operations on its inputs (a1, b1) and (a2, b2). The basic-block vectorizer may combine the following function into vector operations.

```
void foo(int a1, int a2, int b1, int b2, int *A) {
  A[0] = a1*(a1 + b1);
  A[1] = a2*(a2 + b2);
  A[2] = a1*(a1 + b1);
  A[3] = a2*(a2 + b2);
}
```
