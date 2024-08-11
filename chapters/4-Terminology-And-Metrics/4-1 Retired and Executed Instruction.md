

## Retired vs. Executed Instruction

Modern processors typically execute more instructions than the program flow requires. This happens because some instructions are executed speculatively, as discussed in [@sec:SpeculativeExec]. For most instructions, the CPU commits results once they are available, and all preceding instructions have already been retired. But for instructions executed speculatively, the CPU keeps their results without immediately committing their results. When the speculation turns out to be correct, the CPU unblocks such instructions and proceeds as normal. But when the speculation turns out to be wrong, the CPU throws away all the changes done by speculative instructions and does not retire them. So, an instruction processed by the CPU can be executed but not necessarily retired. Taking this into account, we can usually expect the number of executed instructions to be higher than the number of retired instructions.

There is an exception. Certain instructions are recognized as idioms and are resolved without actual execution. Some examples of this are NOP, move elimination and zeroing, as discussed in [@sec:uarchBE]. Such instructions do not require an execution unit but are still retired. So, theoretically, there could be a case when the number of retired instructions is higher than the number of executed instructions.

There is a performance monitoring counter (PMC) in most modern processors that collects the number of retired instructions. There is no performance event to collect executed instructions, though there is a way to collect executed and retired *$\mu$ops* as we shall see soon. The number of retired instructions can be easily obtained with Linux `perf` by running:

```bash
$ perf stat -e instructions ./a.exe
  2173414  instructions  #    0.80  insn per cycle 
# or just simply run:
$ perf stat ./a.exe
```
