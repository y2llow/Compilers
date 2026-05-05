#include <stdio.h>

int power(int base, int exp);

int main() {
    printf("%d", power(2, 8));
    return 0;
}

int power(int base, int exp) {
    int result = 1;
    int i = 0;
    while (i < exp) {
        result = result * base;
        i = i + 1;
    }
    return result;
}