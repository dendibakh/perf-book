---
typora-root-url: ..\..\img
---

## Compile-Time Computations

If a portion of a program does some calculations that don't depend on the input, it can be precomputed ahead of time instead of doing it in the runtime.  Modern optimizing compilers already move a lot of computations into compile-time, especially trivial cases like `int x = 2 * 10` into `int x = 20`. Although, they cannot handle more complicated calculations at compile time if they involve branches, loops, function calls. C++ language provides features that allow us to make sure that certain calculations happen at compile time.

In C++, it's possible to move computations into compile-time with various metaprogramming techniques. Before `C++11/14`, developers were using templates to achieve this result. It is theoretically possible to express any algorithm with template metaprogramming; however, this method tends to be syntactically obtuse and often compile quite slowly. Still, it was a success that enabled a new class of optimizations. Fortunately, metaprogramming gradually becomes a lot simpler with every new C++ standard. The `C++14` standard allows having `constexpr` functions, and the `C++17` standard provides compile-time branches with the `if constexpr` keyword. This new way of metaprogramming allows doing many computations in compile-time without sacrificing code readability. [@fogOptimizeCpp, Chapter 15 Metaprogramming]

An example of optimizing an application by moving computations into compile-time is shown in [@lst:PrimesCompileTime]. Suppose a program involves a test for a number being prime. If we know that a large portion of tested numbers is less than `1024`, we can precompute the results ahead of time and keep them in a `constexpr` array `primes`. At runtime, most of the calls of `isPrime` will involve just one load from the `primes` array, which is much cheaper than computing it at runtime.

Listing: Precomputing prime numbers in compile-time

~~~~ {#lst:PrimesCompileTime .cpp}
constexpr unsigned N = 1024;

// function pre-calculates first N primes in compile-time
constexpr std::array<bool, N> sieve() {
  std::array<bool, N> Nprimes{true};
  Nprimes[0] = Nprimes[1] = false;
  for(long i = 2; i < N; i++)
    Nprimes[i] = true;
  for(long i = 2; i < N; i++) {
    if (Nprimes[i])
      for(long k = i + i; k < N; k += i)
        Nprimes[k] = false;
  }
  return Nprimes;
}

constexpr std::array<bool, N> primes = sieve();

bool isPrime(unsigned value) {
  // primes is accessible both in compile-time and runtime
  static_assert(primes[97], "");
  static_assert(!primes[98], "");
  if (value < N)
    return primes[value];
  // fall back to computing in runtime
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
