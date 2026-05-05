#include <stdio.h>

int multiply(int a, int b);  // Forward declaration

int main() {
    printf("%d", multiply(4, 5));
    return 0;
}

int multiply(int a, int b) {  // Definition later
    return a * b;
}