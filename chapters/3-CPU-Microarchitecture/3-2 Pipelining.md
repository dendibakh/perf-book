## Pipelining

Pipelining is a foundational technique used to make CPUs fast, wherein multiple instructions overlap during their execution. Pipelining in CPUs drew inspiration from automotive assembly lines. The processing of instructions is divided into stages. The stages operate in parallel, working on different parts of different instructions. DLX is a relatively simple architecture designed by John L. Hennessy and David A. Patterson in 1994. As defined in [@Hennessy], it has a 5-stage pipeline which consists of:

1. Instruction fetch (IF)
2. Instruction decode (ID)
3. Execute (EXE)
4. Memory access (MEM)
5. Write back (WB)

![Simple 5-stage pipeline diagram.](../../img/uarch/Pipelining.png){#fig:Pipelining width=80%}

Figure @fig:Pipelining shows an ideal pipeline view of the 5-stage pipeline CPU. In cycle 1, instruction x enters the IF stage of the pipeline. In the next cycle, as instruction x moves to the ID stage, the next instruction in the program enters the IF stage, and so on. Once the pipeline is full, as in cycle 5 above, all pipeline stages of the CPU are busy working on different instructions. Without pipelining, the instruction `x+1` couldn't start its execution until after instruction `x` had finished its work.

Modern high-performance CPUs have multiple pipeline stages, often ranging from 10 to 20 (sometimes more), depending on the architecture and design goals. This involves a much more complicated design than a simple 5-stage pipeline introduced earlier. For example, the decode stage may be split into several new stages. We may also add new stages before the execute stage to buffer decoded instructions and so on.

The *throughput* of a pipelined CPU is defined as the number of instructions that complete and exit the pipeline per unit of time. The *latency* for any given instruction is the total time through all the stages of the pipeline. Since all the stages of the pipeline are linked together, each stage must be ready to move to the next instruction in lockstep. The time required to move an instruction from one stage to the next defines the basic machine *cycle* or clock for the CPU. The value chosen for the clock for a given pipeline is defined by the slowest stage of the pipeline. CPU hardware designers strive to balance the amount of work that can be done in a stage as this directly affects the frequency of operation of the CPU.

In real implementations, pipelining introduces several constraints that limit the nicely-flowing execution illustrated in Figure @fig:Pipelining. Pipeline hazards prevent the ideal pipeline behavior, resulting in stalls. The three classes of hazards are structural hazards, data hazards, and control hazards. Luckily for the programmer, in modern CPUs, all classes of hazards are handled by the hardware.

\lstset{linewidth=10cm}

* **Structural hazards**: are caused by resource conflicts, i.e., when there are two instructions competing for the same resource. An example of such a hazard is when two 32-bit addition instructions are ready to execute in the same cycle, but there is only one execution unit available in that cycle. In this case, we need to choose which one of the two instructions to execute and which one will be executed in the next cycle. To a large extent, they could be eliminated by replicating hardware resources, such as using multiple execution units, instruction decoders, multi-ported register files, etc. However, this could potentially become quite expensive in terms of silicon area and power.

* **Data hazards**: are caused by data dependencies in the program and are classified into three types:

  A *read-after-write* (RAW) hazard requires a dependent read to execute after a write. It occurs when instruction `x+1` reads a source before previous instruction `x` writes to the source, resulting in the wrong value being read. CPUs implement data forwarding from a later stage of the pipeline to an earlier stage (called "*bypassing*") to mitigate the penalty associated with the RAW hazard. The idea is that results from instruction `x` can be forwarded to instruction `x+1` before instruction `x` is fully completed. If we take a look at the example:

  ```
  R1 = R0 ADD 1
  R2 = R1 ADD 2
  ```

  There is a RAW dependency for register R1. If we take the value directly after the addition `R0 ADD 1` is done (from the `EXE` pipeline stage), we don't need to wait until the `WB` stage finishes (when the value will be written to the register file). Bypassing helps to save a few cycles. The longer the pipeline, the more effective bypassing becomes.

  A *write-after-read* (WAR) hazard requires a dependent write to execute after a read. It occurs when an instruction writes a register before an earlier instruction reads the source, resulting in the wrong new value being read. A WAR hazard is not a true dependency and can be eliminated by a technique called *register renaming*. It is a technique that abstracts logical registers from physical registers. CPUs support register renaming by keeping a large number of physical registers. Logical (*architectural*) registers, the ones that are defined by the ISA, are just aliases over a wider register file. With such decoupling of the architectural state, solving WAR hazards is simple: we just need to use a different physical register for the write operation. For example:

  ```
  ; machine code, WAR hazard              ; after register renaming 
  ; (architectural registers)             ; (physical registers)
  R1 = R0 ADD 1                  =>       R101 = R100 ADD 1
  R0 = R2 ADD 2                           R103 = R102 ADD 2
  ```

  In the original assembly code, there is a WAR dependency for register `R0`. For the code on the left, we cannot reorder the execution of the instructions, because it could leave the wrong value in `R1`. However, we can leverage our large pool of physical registers to overcome this limitation. To do that we need to rename all the occurrences of the `R0` register starting from the write operation (`R0 = R2 ADD 2`) and below to use a free register. After renaming, we give these registers new names that correspond to physical registers, say `R103`. By renaming registers, we eliminated a WAR hazard in the initial code, and we can safely execute the two operations in any order.

  A *write-after-write* (WAW) hazard requires a dependent write to execute after a write. It occurs when an instruction writes to a register before an earlier instruction writes to the same register, resulting in the wrong value being stored. WAW hazards are also eliminated by register renaming, allowing both writes to execute in any order while preserving the correct final result. Below is an example of eliminating WAW hazards.

  ```
  ; machine code, WAW hazard              ; after register renaming
  (architectural registers)               (physical registers)
  R1 = R0 ADD 1                  =>       R101 = R100 ADD 1
  R2 = R1 SUB R3  ; RAW                   R102 = R101 SUB R103 ; RAW
  R1 = R0 MUL 3   ; WAW and WAR           R104 = R100 MUL 3
  ```

  You will see similar code in many production programs. In our example, `R1` keeps the temporary result of the `ADD` operation. Once the `SUB` instruction is complete, `R1` is immediately reused to store the result of the `MUL` operation. The original code on the left features all three types of data hazards. There is a RAW dependency over `R1` between `ADD` and `SUB`, and it must survive register renaming. Also, we have WAW and WAR hazards over the same `R1` register for the `MUL` operation. Again, we need to rename registers to eliminate those two hazards. Notice that after register renaming we have a new destination register (`R104`) for the `MUL` operation. Now we can safely reorder `MUL` with the other two operations.

* **Control hazards**: are caused due to changes in the program flow. They arise from pipelining branches and other instructions that change the program flow. The branch condition that determines the direction of the branch (taken vs. not taken) is resolved in the execute pipeline stage. As a result, the fetch of the next instruction cannot be pipelined unless the control hazard is eliminated. Techniques such as dynamic branch prediction and speculative execution described in the next section are used to mitigate control hazards.

\lstset{linewidth=\textwidth}
