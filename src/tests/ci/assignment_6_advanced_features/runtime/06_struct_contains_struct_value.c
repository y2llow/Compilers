#include <stdio.h>

struct Packet {
    int length;
    int code;
};

struct Header {
    int src;
    struct Packet data;
};

int main() {
    struct Header h;

    h.src = 3;
    h.data.length = 40;
    h.data.code = 2;

    printf("%d", h.src + h.data.length + h.data.code);
    return 0;
}