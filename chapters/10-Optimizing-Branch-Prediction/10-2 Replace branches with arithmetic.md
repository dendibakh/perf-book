## Replace Branches with Arithmetic

In some scenarios, branches can be replaced with arithmetic. The code in [@lst:LookupBranches], can also be rewritten using a simple arithmetic formula, as shown in [@lst:ArithmeticBranches]. Notice, that for this code, the Clang-17 compiler replaced expensive division with much cheaper multiplication and right shift operations.

Listing: Replacing branches with arithmetic.

~~~~ {#lst:ArithmeticBranches .cpp}
int8_t mapToBucket(unsigned v) {             │    mov al, -1
  constexpr unsigned BucketRangeMax = 50;    │    cmp edi, 49
  if (v < BucketRangeMax)                    │    ja .exit
    return v / 10;                           │    movzx eax, dil
  return -1;                                 │    imul eax, eax, 205
}                                            │    shr eax, 11
                                             │  .exit:
                                             │    ret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another common way is to replace conditional branches with a combination of bitwise operations and arithmetic that leverage boolean logic. Instead of branching, you can use a mask that evaluates to either 0 or 1 (or 0xFFFFFFFF in some cases) and then select between two possible values. [@lst:BrancheslessLFSR] shows an example of replacing branches in a Linear Feedback Shift Register (LFSR) code. LFSRs are widely used in communication, cryptography, and other systems due to their ability to generate sequences that exhibit properties similar to randomness. LFSRs are initialized with a seed and the output is fed back into the LFSR to produce the next number.

Listing: Replacing branches in LFSR.

~~~~ {#lst:BrancheslessLFSR .cpp}
int lfsr(int x) {                     int lfsr(int x) {
  if (x < 0)                            x = (x << 1) ^ ((x >> 31) & CONSTANT);
    x = (x << 1) ^ CONSTANT;    =>      return x;
  else                                }
    x = (x << 1);
  return x;                 
}                       

; x86 machine code                    ; x86 machine code
lea     ecx, [rdi + rdi]              lea     eax, [rdi + rdi]
mov     eax, ecx                      sar     edi, 31
xor     eax, #CONSTANT                and     edi, #CONSTANT
test    edi, edi                      xor     eax, edi
cmovns  eax, ecx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In our example, we shift left the input value regardless if it is positive or negative. In addition, if the input value is negative, we also XOR it with a constant (exact value is irrelevant for this scenario). In the modified version, we leverage the fact that arithmetic right shift (`>>`) turns the sign of `x` (the high order bit) into a mask of all zeros or all ones. The subsequent AND (`&`) operation produces either zero or the desired constant. The original version of the function takes ~4 cycles, while the modified version takes only 3 cycles. It's worth mentioning that Clang 17 compiler replaced the branch with a conditional select (CMOVNS) instruction, which we will cover in the next section. Nevertheless, with some smart bit manipulation we were able to improve it even further.

As of the year 2024, compilers are usually unable to find these shortcuts on their own, so it is up to the programmer to do it manually. If you can find a way to replace a branch with arithmetic, you will likely see a performance improvement. We cannot cover all the various tricks, but you can find more of them in other books, for example [@HackersDelight].