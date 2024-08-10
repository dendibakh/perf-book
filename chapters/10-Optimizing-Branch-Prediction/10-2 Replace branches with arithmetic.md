## Replace Branches with Arithmetic

In some scenarios, branches can be replaced with arithmetic. The code in [@lst:LookupBranches], can also be rewritten using a simple arithmetic formula, as shown in [@lst:ArithmeticBranches]. For this code, the Clang-17 compiler replaces expensive division with a much cheaper multiplication operation.

Listing: Replacing branches with arithmetic.

~~~~ {#lst:ArithmeticBranches .cpp}
int8_t mapToBucket(unsigned v) {
  constexpr unsigned BucketRangeMax = 50;
  if (v < BucketRangeMax)
    return v / 10;
  return -1;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of the year 2023, compilers are usually unable to find these shortcuts on their own, so it is up to the programmer to do it manually. If you can find a way to replace a branch with arithmetic, you will likely see a performance improvement. Unfortunately, this is not always possible. 
