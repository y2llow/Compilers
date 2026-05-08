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
    struct Header headers[2];

    headers[0].src = 1;
    headers[0].data.length = 10;
    headers[0].data.code = 2;

    headers[1].src = 3;
    headers[1].data.length = 20;
    headers[1].data.code = 4;

    printf("%d",
        headers[0].src +
        headers[0].data.length +
        headers[0].data.code +
        headers[1].src +
        headers[1].data.length +
        headers[1].data.code
    );

    return 0;
}