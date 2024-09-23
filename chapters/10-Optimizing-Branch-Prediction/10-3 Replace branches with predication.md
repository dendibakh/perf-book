## Replace Branches with Selection {#sec:BranchlessSelection}

Some branches could be effectively eliminated by executing both parts of the branch and then selecting the right result. An example of code when such transformation might be profitable is shown in [@lst:ReplaceBranchesWithSelection]. If TMA suggests that the `if (cond)` branch has a very high number of mispredictions, you can try to eliminate the branch by doing the transformation shown on the right.

Listing: Replacing Branches with Selection.

~~~~ {#lst:ReplaceBranchesWithSelection .cpp}
int a;                                             int x = computeX();
if (cond) { /* frequently mispredicted */   =>     int y = computeY();
  a = computeX();                                  int a = cond ? x : y;
} else {                                           foo(a);
  a = computeY();
}
foo(a);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the code on the right, the compiler can replace the branch that comes from the ternary operator, and generate a `CMOV` x86 instruction instead. A `CMOVcc` instruction checks the state of one or more of the status flags in the `EFLAGS` register (`CF, OF, PF, SF` and `ZF`) and performs a move operation if the flags are in a specified state or condition. A similar transformation can be done for floating-point numbers with `FCMOVcc, VMAXSS/VMINSS` instructions. In the ARM ISA, there is `CSEL` (conditional selection) instruction, but also `CSINC` (select and increment), `CSNEG` (select and negate), and a few other conditional instructions.

Listing: Replacing Branches with Selection - x86 assembly code.

~~~~ {#lst:ReplaceBranchesWithSelectionAsm .bash}
# original version              # branchless version
400504: test ebx,ebx            400537: mov eax,0x0
400506: je 400514               40053c: call <computeX> # compute x; a = x
400508: mov eax,0x0             400541: mov ebp,eax     # ebp = x
40050d: call <computeX>    =>   400543: mov eax,0x0
400512: jmp 40051e              400548: call <computeY> # compute y; a = y
400514: mov eax,0x0             40054d: test ebx,ebx    # test cond
400519: call <computeY>         40054f: cmovne eax,ebp  # override a with x if needed
40051e: mov edi,eax             400552: mov edi,eax
400521: call <foo>              400554: call <foo>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[@lst:ReplaceBranchesWithSelectionAsm] shows assembly listings for the original and the branchless version. In contrast with the original version, the branchless version doesn't have jump instructions. However, the branchless version calculates both `x` and `y` independently, and then selects one of the values and discards the other. While this transformation eliminates the penalty of a branch misprediction, it is doing more work than the original code. 

We already know that the branch in the original version on the left is hard to predict. This is what motivates us to try a branchless version in the first place. In this example, the performance gain of this change depends on the characteristics of the `computeX` and `computeY` functions. If the functions are small[^1] and the compiler can inline them, then selection might bring noticeable performance benefits. If the functions are big[^2], it might be cheaper to take the cost of a branch mispredict than to execute both `computeX` and `computeY` functions. Ultimately, performance measurements always decide which version is better.

Take a look at [@lst:ReplaceBranchesWithSelectionAsm] one more time. On the left, a processor can predict, for example, that the `je 400514` branch will be taken, speculatively call `computeY`, and start running code from the function `foo`. Remember, branch prediction usually happens many cycles before we know the actual outcome of the branch. By the time we start resolving the branch, we could be already halfway through the `foo` function, despite it is still speculative. If we are correct, we've saved a lot of cycles. If we are wrong, we have to take the penalty and start over from the correct path. In the latter case, we don't gain anything from the fact that we have already completed a portion of `foo`, it all must be thrown away. If the mispredictions occur too often, the recovering penalty outweighs the gains from speculative execution.

With conditional selection, it is different. There are no branches, so the processor doesn't have to speculate. It can execute `computeX` and `computeY` functions in parallel. However, it cannot start running the code from `foo` until it computes the result of the `CMOVNE` instruction since `foo` uses it as an argument (data dependency). When you use conditional select instructions, you convert a control flow dependency into a data flow dependency. 

To sum it up, for small `if ... else` statements that perform simple operations, conditional selects can be more efficient than branches, but only if the branch is hard to predict. So don't force the compiler to generate conditional selects for every conditional statement. For conditional statements that are always correctly predicted, having a branch instruction is likely an optimal choice, because you allow the processor to speculate (correctly) and run ahead of the actual execution. And don't forget to measure the impact of your changes.

Without profiling data, compilers don't have visibility into the misprediction rates. As a result, they usually prefer to generate branch instructions by default. Compilers are conservative at using selection and may resist generating `CMOV` instructions even in simple cases. Again, the tradeoffs are complicated, and it is hard to make the right decision without the runtime data.[^4] Starting from Clang-17, the compiler now honors a `__builtin_unpredictable` hint for the x86 target, which indicates to the compiler that a branch condition is unpredictable. It can help influence the compiler's decision but does not guarantee that the `CMOV` instruction will be generated. For example:

```cpp
int a;
if (__builtin_unpredictable(cond)) { 
  a = computeX();
} else {
  a = computeY();
}
```

[^1]: Just a handful of instructions that can be completed in a few cycles.
[^2]: More than twenty instructions that take more than twenty cycles.
[^4]: Hardware-based PGO (see [@sec:secPGO]) will be a huge step forward here.
