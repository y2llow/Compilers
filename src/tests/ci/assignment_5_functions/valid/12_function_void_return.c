#include <stdio.h>

void print_message(int times) {
    int i = 0;
    while (i < times) {
        printf("Hello\n");
        i = i + 1;
    }
}

int main() {
    print_message(3);
    return 0;
}