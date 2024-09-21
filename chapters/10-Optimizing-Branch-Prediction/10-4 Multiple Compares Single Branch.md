## Multiple Tests Single Branch {#sec:MultipleCmpSingleBranch}

The last technique that we discuss in this chapter aims at minimizing the dynamic number of branch instructions by combining multiple tests. The main idea here is to avoid executing a branch for every element of a large array. Instead, the goal is to perform multiple tests simultaneously, which primarily involves using SIMD instructions. The result of this is a vector mask that can be converted into a byte mask, which enables us eliminate many unnecessary branches as you will see shortly. You may encounter these technique being used in SIMD implementations of various algorithms such as JSON/HTML parsing, media codecs and others.

[@lst:LongestLineNaive] shows a function that finds the longest line in an input string by testing one character at a time. We go through the input string and search for end-of-line (`eol`) characters (`\n`, 0x0a in ASCII). For every found `eol` character we check if the current line is the longest, and reset the lenght of the current line to zero. This code will execute one branch instruction for every character.[^1]

Listing: Find the longest line (one character at a time).

~~~~ {#lst:LongestLineNaive .cpp .numberLines}
uint32_t longestLine(const std::string &str) {
  uint32_t maxLen = 0;
  uint32_t curLen = 0;
  for (auto s : str) {
    if (s == '\n') {
      maxLen = std::max(curLen, maxLen);
      curLen = 0;
    } else {
      curLen++;
    }
  }
  // if no end-of-line in the end
  maxLen = std::max(curLen, maxLen);
  return maxLen;
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider the alternative implementation shown in [@lst:LongestLineSIMD] that tests eight characters at a time. You will typically see this idea implemented using compiler instrinsics (see [@sec:secIntrinsics]), however we decided to show a standard C++ code for clarity. This exact case is featured in one of Performance Ninja's lab assignments,[^2] so you can try writing SIMD code yourself. Keep in mind, this in not a complete code of the solution as it misses a few corner cases; we provide this code just to illustrate the idea.

Listing: Find the longest line (8 characters at a time).

~~~~ {#lst:LongestLineSIMD .cpp .numberLines}
uint32_t longestLine(const std::string &str) {
  uint32_t maxLen = 0;
  const uint64_t eol = 0x0a0a0a0a0a0a0a0a;
  auto *buf = str.data();
  uint32_t lineBeginPos = 0;
  for (uint32_t pos = 0; pos + 7 < str.size(); pos += 8) {
    // Load 8-byte chunk of the input string.
    uint64_t vect = *((const uint64_t*)(buf + pos));
    // Check all characters in this chunk.
    uint8_t mask = compareBytes(vect, eol);
    while (mask) {
      uint16_t eolPos = tzcnt(mask);
      // Compute the length of the current string.
      uint32_t curLen = (pos - lineBeginPos) + eolPos;
      // New line starts with the character after '\n'
      lineBeginPos += curLen + 1;
      // Is this line the longest?
      maxLen = std::max(curLen, maxLen);
      // Shift the mask to check if we have more '\n'
      mask >>= eolPos + 1;
    }
  }
  // process remainder (not shown)
  return maxLen;
}

uint8_t compareBytes(uint64_t a, uint64_t b) {
  // Perform byte-wise comparison of a and b.
  // Produce a bit mask with result of comparisons:
  // one if bytes are equal, zero if different.
}

uint8_t tzcnt(uint8_t mask) {
  // Count the number of trailing zero bits in the mask.
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We start of by preparing an 8-byte mask of `eol` symbols. The inner loop loads eight characters of the input string and performs byte-wise compare of these characters with the `eol` mask. Vectors in modern processors contain 16/32/64 bytes, so we can process even more characters simultaneously. The result of those eight comparisons is an 8-bit mask with either 0 or 1 in the corresponding position (see `compareBytes`). For example, when comparing `0x00FF0a00FF0aFF00` and `0x0a0a0a0a0a0a0a0a`, we will get `0b00100100` as a result. With x86 and ARM ISAs, the function `compareBytes` can be implemented using two vector instructions.[^4]

If the mask is zero, that means there are no `eol` characters in the current chunk and we can skip it (see line 11). This is a critical optimization that provides large speedups for input strings with long lines. If a mask is not zero, that means there are `eol` characters and we need to find their positions. To do so, we use the `tzcnt` function, that counts the number of trailing zero bits in an 8-bit mask. For example, for the mask `0b00100100`, it will return 2. We use the position of the rightmost set bit in the mask to calculate the length of the current line. We repeat until there are no set bits in the mask and then start processing the next chunk. Most ISAs support implementing the `tzcnt` function with a single instruction.[^3]

We tested this idea using AVX2 implementation on several different inputs, including textbooks, whitepapers and source code files. The result was 5--6 times fewer branch instructions and more than 4x better performance when running on Intel Core i7-1260P (12th Gen, Alderlake).

[^1]: Assuming that compiler will avoid generating branch instructions for `std::max`.
[^2]: Performance Ninja: compiler intrinsics 2 - [https://github.com/dendibakh/perf-ninja/tree/main/labs/core_bound/compiler_intrinsics_2](https://github.com/dendibakh/perf-ninja/tree/main/labs/core_bound/compiler_intrinsics_2).
[^3]: Although in x86, there is no version of `TZCNT` instruction that supports 8-bit inputs.
[^4]: For example, with AVX2 (256-bit vectors), you can use `VPCMPEQB` and `VPMOVMSKB` instructions.