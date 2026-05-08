#include <stdio.h>

struct Packet {
    int length;
    int code;
};

int main() {
    struct Packet packets[2];

    packets[0].length = 10;
    packets[0].code = 1;

    packets[1].length = 20;
    packets[1].code = 2;

    printf("%d", packets[0].length + packets[0].code + packets[1].length + packets[1].code);

    return 0;
}