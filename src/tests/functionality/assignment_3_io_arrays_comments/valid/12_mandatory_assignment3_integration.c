#include <stdio.h>
/* mandatory integration: comments + arrays + strings + printf */
int main() {
    int values[3] = {3, 45, -9};
    int matrix[2][2] = {{1, 2}, {3, 4}};
    char *label = "result";
    int result = values[0] + matrix[1][1]; // original statement comment should be visible in LLVM
    printf("%s: %d\n", label, result);
    return result;
}
