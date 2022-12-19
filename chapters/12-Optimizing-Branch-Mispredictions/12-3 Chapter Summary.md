---
typora-root-url: ..\..\img
---

## Chapter Summary

* Modern processors are very good at predicting branch outcomes. So, I recommend starting the work on fixing branch mispredictions only when the TMA report points to a high `Bad Speculation` metric.
* When the outcome pattern becomes hard for the CPU branch predictor to follow, the performance of the application may suffer. In this case, the branchless version of an algorithm can be better. In this chapter, we showed how branches could be replaced with lookup tables and predication. In some situations, it is also possible to use compiler intrinsics to eliminate branches, as shown in [@IntelAvoidingBrMisp].
* Branchless algorithms are not universally beneficial. Always measure to find out if that works better in your case.


