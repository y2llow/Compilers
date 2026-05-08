#include <stdio.h>
int main() {
    int dec = 42;
    int hex = 255;
    float f = 3.5;
    char c = 'A';
    char *s = "text";
    printf("d=%d x=%x s=%s f=%f c=%c %%\n", dec, hex, s, f, c);
    return 0;
}
