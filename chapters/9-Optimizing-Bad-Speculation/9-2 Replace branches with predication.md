---
typora-root-url: ..\..\img
---

## Replace branches with predication

Some branches could be effectively eliminated by executing both parts of the branch and then selecting the right result (predication). Example[^1] of code when such transformation might be profitable is shown on [@lst:PredicatingBranches1]. If TMA suggests that the `if (cond)` branch has a very high number of mispredictions, one can try to eliminate the branch by doing the transformation shown on [@lst:PredicatingBranches2].

Listing: Predicating branches: baseline version.

~~~~ {#lst:PredicatingBranches1 .cpp}
int a;
if (cond) { // branch has high misprediction rate
  a = computeX();
} else {
  a = computeY();
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Listing: Predicating branches: branchless version.

~~~~ {#lst:PredicatingBranches2 .cpp}
int x = computeX();
int y = computeY();
int a = cond ? x : y;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the version of code in [@lst:PredicatingBranches2], the compiler can get rid of the branch and generate `CMOV` instruction[^2] instead. The `CMOVcc` instructions check the state of one or more of the status flags in the `EFLAGS` register (`CF, OF, PF, SF` and `ZF`) and perform a move operation if the flags are in a specified state (or condition). [@IntelSDM, Volume 2] Below are the two assembly listings for the baseline and improved version, respectively:

```bash
# baseline version
400504:   test   edi,edi 
400506:   je     400514      # branch on cond
400508:   mov    eax,0x0
40050d:   call   <computeX>
400512:   jmp    40051e
400514:   mov    eax,0x0
400519:   call   <computeY>
40051e:   mov    edi,eax

  =>

# branchless version
400537:   mov    eax,0x0
40053c:   call   <computeX>  # compute x
400541:   mov    ebp,eax     # assign x to a
400543:   mov    eax,0x0
400548:   call   <computeY>  # compute y
40054d:   test   ebx,ebx     # test cond
40054f:   cmovne eax,ebp     # override a with y if needed
```

The modified assembly sequence doesn't have original branch instruction. However, in the second version, both `x` and `y` are calculated independently, and then only one of the values is selected. While this transformation eliminates the penalty of branch mispredictions, it is potentially doing more work than the original code. Performance improvement, in this case, very much depends on the characteristics of `computeX` and `computeY` functions. If the functions are small and the compiler is able to inline them, then it might bring noticeable performance benefits. If the functions are big, it might be cheaper to take the cost of a branch misprediction than to execute both functions. 

It is important to note that predication does not always benefit the performance of the application. The issue with predication is that it limits the parallel execution capabilities of the CPU. For the code snippet in [@lst:PredicatingBranches1], the CPU can choose, say, `true` branch of the `if` condition, and continue speculative execution of the code with the value of `a = computeX() `. If, for example, there is a subsequent load that uses `a` to index an element in an array, this load can be issued well before we know the true outcome of the `if` branch. This type of speculation is not possible for the code in the [@lst:PredicatingBranches2] since the CPU cannot issue a load that uses `a` before the `CMOVNE` instruction completes.

The typical example of the tradeoffs involved when choosing between the standard and the branchless versions of the code is binary search[^3]:

* For a search over a large array that doesn't fit in CPU caches, a branch-based binary search version performs better because the penalty of a branch misprediction is low comparing to the latency of memory accesses (which are high because of the cache misses). Because of the branches in place, the CPU can speculate on their outcome, which allows loading the array element from the current iteration and the next at the same time. It doesn't end there: the speculation continues, and you might have multiple loads in flight at the same time.
* The situation is reversed for small arrays that fit in CPU caches. The branchless search still has all the memory accesses serialized, as explained earlier. But this time, the load latency is small (only a handful of cycles) since the array fits in CPU caches. The branch-based binary search suffers constant mispredictions, which cost on the order of ~20 cycles. In this case, the cost of misprediction is much more than the cost of memory access, so that the benefits of speculative execution are hindered. The branchless version usually ends up being faster in this case.

The binary search is a neat example that shows how one can reason about when choosing between standard and branchless implementation. The real-world scenario can be more difficult to analyze, so again, measure to find out if it would be beneficial to replace branches in your case.

[^1]: Example of replacing branches with CMOV - [https://easyperf.net/blog/2019/04/10/Performance-analysis-and-tuning-contest-2#fighting-branch-mispredictions-9](https://easyperf.net/blog/2019/04/10/Performance-analysis-and-tuning-contest-2#fighting-branch-mispredictions-9)
[^2]: Similar transformation can be done for floating-point numbers with `FCMOVcc,VMAXSS/VMINSS` instruction.
[^3]: See more detailed discussion here: [https://stackoverflow.com/a/54273248](https://stackoverflow.com/a/54273248).
