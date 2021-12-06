---
typora-root-url: ..\..\img
---

## Detecting Slow FP Arithmetic {#sec:SlowFPArith}

For applications that operate with floating-point values, there is some probability of hitting an exceptional scenario when the FP values become [denormalized](https://en.wikipedia.org/wiki/Denormal_number)[^1]. Operations on denormal values could be easy `10` times slower or more. When CPU handles instruction that tries to do arithmetic operation on denormal FP values, it requires special treatment for such cases. Since it is exceptional situation, CPU requests a microcode [assist](https://software.intel.com/en-us/vtune-help-assists)[^10]. Microcode Sequencer (MSROM) will then feed the pipeline with lots of uops (see [@sec:sec_UOP]) for handling such a scenario.

TMA methodology classifies such bottlenecks under the `Retiring` category. This is one of the situations when high Retiring doesn't mean a good thing. Since operations on denormal values likely represent unwanted behavior of the program, one can just collect the `FP_ASSIST.ANY` performance counter. The value should be close to zero. An example of a program that does denormal FP arithmetics and thus experiences many FP assists is presented on easyperf [blog](https://easyperf.net/blog/2018/11/08/Using-denormal-floats-is-slow-how-to-detect-it)[^2]. C++ developers can prevent their application fall into operations with subnormal values by using [`std::isnormal()`](https://en.cppreference.com/w/cpp/numeric/math/isnormal)[^3]function. Alternatively, one can change the mode of SIMD floating-point operations, enabling "flush-to-zero" (FTZ) and "denormals-are-zero" (DAZ) flags in the CPU control register[^5], preventing SIMD instructions from producing denormalized numbers[^4]. Disabling denormal floats at the code level can be done using dedicated macros, which can vary for different compilers[^6].

[^1]: Denormal number - [https://en.wikipedia.org/wiki/Denormal_number](https://en.wikipedia.org/wiki/Denormal_number).
[^2]: Denormal FP arithmetics - [https://easyperf.net/blog/2018/11/08/Using-denormal-floats-is-slow-how-to-detect-it](https://easyperf.net/blog/2018/11/08/Using-denormal-floats-is-slow-how-to-detect-it).
[^3]: `std::isnormal()` - [https://en.cppreference.com/w/cpp/numeric/math/isnormal](https://en.cppreference.com/w/cpp/numeric/math/isnormal).
[^4]: However, FTZ and DAZ modes make such operations not being compliant with the IEEE standard.
[^5]: See more about FTZ and DAZ modes here: [https://software.intel.com/content/www/us/en/develop/articles/x87-and-sse-floating-point-assists-in-ia-32-flush-to-zero-ftz-and-denormals-are-zero-daz.html](https://software.intel.com/content/www/us/en/develop/articles/x87-and-sse-floating-point-assists-in-ia-32-flush-to-zero-ftz-and-denormals-are-zero-daz.html).
[^6]: See this wiki page as a starting point: [https://en.wikipedia.org/wiki/Denormal_number#Disabling_denormal_floats_at_the_code_level](https://en.wikipedia.org/wiki/Denormal_number#Disabling_denormal_floats_at_the_code_level).
[^10]: CPU assists - [https://software.intel.com/en-us/vtune-help-assists](https://software.intel.com/en-us/vtune-help-assists).
