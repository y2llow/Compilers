#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int main() {
    int result = add(multiply(2, 3), 4);  // (2*3) + 4 = 10
    printf("%d", result);
    return 0;
}