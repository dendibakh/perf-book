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

As of the year 2024, compilers are usually unable to find these shortcuts on their own, so it is up to the programmer to do it manually. If you can find a way to replace a frequently mispredicted branch with arithmetic, you will likely see a performance improvement.
