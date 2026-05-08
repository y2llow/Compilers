#include <stdio.h>
/* This block comment should be retained in the AST/LLVM if comment retention is implemented. */
int main() {
    int x = 5; // this source statement should appear as a comment near the first LLVM instruction
    x = x + 1;
    printf("x=%d\n", x);
    return x;
}
