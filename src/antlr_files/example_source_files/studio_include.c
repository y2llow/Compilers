#include <stdio.h>

/*
 * My program
 */
int main() {
    int x = 5;
    float y = 3.14;
    char ch = 'A';

    printf("Hello, world!\n");
    printf("x = %d\n", x);
    printf("y = %f\n", y);
    printf("ch = %c\n", ch);
    printf("hex = %x\n", x);

    int input;
    scanf("%d", &input);

    return 0;
}