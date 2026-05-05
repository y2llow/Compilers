#include <stdio.h>


int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int main() {
    printf("%d", add(10, 3));
    printf("%d", subtract(10, 3));
    return 0;
}